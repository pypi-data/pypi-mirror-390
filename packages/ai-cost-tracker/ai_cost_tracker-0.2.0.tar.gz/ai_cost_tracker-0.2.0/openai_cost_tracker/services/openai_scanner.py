#!/usr/bin/env python3
"""
OpenAI Usage Scanner
Scans entire git folder to find all files and services using OpenAI API
"""

import os
import re
import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class OpenAIUsage:
    """Record of OpenAI API usage in a file"""
    file_path: str
    file_type: str  # "python", "bash", "javascript", etc.
    service_name: str
    api_key_source: str  # "env", "hardcoded", "config", "unknown"
    api_key_hash: Optional[str] = None  # Hash of detected key (if found)
    openai_imports: List[str] = None  # List of OpenAI imports
    usage_patterns: List[str] = None  # Patterns found (OpenAI(), client.chat, etc.)
    env_vars: List[str] = None  # Environment variables used
    direct_api_calls: int = 0  # Count of direct API calls
    wrapped_usage: bool = False  # Using tracked wrapper
    
    def __post_init__(self):
        if self.openai_imports is None:
            self.openai_imports = []
        if self.usage_patterns is None:
            self.usage_patterns = []
        if self.env_vars is None:
            self.env_vars = []


class OpenAIScanner:
    """Scanner to find OpenAI API usage across codebase"""
    
    def __init__(self, scan_root: str = None, registry_file: Optional[Path] = None):
        """Initialize scanner"""
        if scan_root is None:
            # Default to current directory
            self.scan_root = Path.cwd()
        else:
            self.scan_root = Path(scan_root).expanduser()
        
        if registry_file is None:
            # Default to user's home directory or current directory
            import os
            default_dir = Path.home() / ".openai_cost_tracker"
            if not os.access(Path.home(), os.W_OK):
                default_dir = Path.cwd() / ".openai_cost_tracker"
            self.registry_file = default_dir / "openai_registry.json"
        else:
            self.registry_file = Path(registry_file)
        
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Patterns to find OpenAI usage
        self.patterns = {
            "imports": [
                r"from openai import",
                r"import openai",
                r"from openai\.", 
                r"OpenAI\(|AsyncOpenAI\(",
                r"openai\.",
            ],
            "api_keys": [
                r"OPENAI_API_KEY",
                r"OPENAI_API_KEY\s*=",
                r"api[_-]?key",
                r"sk-[a-zA-Z0-9]{20,}",
            ],
            "usage": [
                r"\.videos\.create",
                r"\.images\.generate",
                r"\.chat\.completions",
                r"\.embeddings\.create",
                r"client\.videos",
                r"client\.images",
                r"client\.chat",
            ],
            "service_files": [
                r"\.service$",
                r"systemd",
            ]
        }
        
        # File extensions to scan
        self.scan_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx",
            ".sh", ".bash", ".zsh",
            ".yaml", ".yml", ".json",
            ".env", ".service",
        }
        
        # Directories to skip
        self.skip_dirs = {
            "__pycache__", "node_modules", ".git", ".venv", "venv",
            "env", ".env", "dist", "build", ".pytest_cache",
            "logs", ".idea", ".vscode", ".DS_Store"
        }
    
    def hash_api_key(self, key: str) -> str:
        """Create hash of API key for identification"""
        if not key:
            return None
        # Remove common prefixes and whitespace
        key = key.strip().strip('"').strip("'")
        if not key.startswith("sk-"):
            return None
        hash_obj = hashlib.sha256(key.encode())
        return hash_obj.hexdigest()[:16]  # First 16 chars
    
    def detect_api_key_in_file(self, file_path: Path) -> Optional[Tuple[str, str]]:
        """Detect API key in file (returns (key_hash, source))"""
        try:
            content = file_path.read_text(errors='ignore')
            
            # Check for hardcoded keys
            hardcoded_match = re.search(r'sk-[a-zA-Z0-9]{20,}', content)
            if hardcoded_match:
                key = hardcoded_match.group(0)
                key_hash = self.hash_api_key(key)
                if key_hash:
                    return (key_hash, "hardcoded")
            
            # Check for env var references
            env_matches = re.findall(r'(?:OPENAI_API_KEY|OPENAI[_-]?API[_-]?KEY)\s*[=:]\s*["\']?([^"\'\s]+)', content)
            if env_matches:
                # Check if it's a real key or just env var name
                for match in env_matches:
                    if match.startswith("sk-"):
                        key_hash = self.hash_api_key(match)
                        if key_hash:
                            return (key_hash, "env")
            
            # Check for config files
            if file_path.suffix in [".json", ".yaml", ".yml"]:
                if "openai" in content.lower() and "key" in content.lower():
                    return (None, "config")
            
        except Exception as e:
            logger.debug(f"Error detecting key in {file_path}: {e}")
        
        return None
    
    def detect_service_name(self, file_path: Path) -> str:
        """Detect service name from file path"""
        path_str = str(file_path)
        
        # Check for common service patterns
        if ".service" in path_str:
            return file_path.stem
        
        # Check for automation services
        if "automation" in path_str:
            if "motivation" in path_str:
                return "automation_service_v2_motivation"
            if "commonsense" in path_str:
                return "automation_service_v2_commonsense"
            if "email" in path_str.lower():
                return "email_watcher_service"
            return "automation_service"
        
        # Check for backend services
        if "backend" in path_str:
            return "backend_api_server"
        
        # Use directory or filename
        parts = file_path.parts
        if len(parts) > 1:
            return f"{parts[-2]}_{parts[-1].replace('.', '_')}"
        
        return file_path.stem
    
    def scan_file(self, file_path: Path) -> Optional[OpenAIUsage]:
        """Scan a single file for OpenAI usage"""
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(errors='ignore')
        except:
            return None
        
        # Quick check if file might use OpenAI
        has_openai = False
        for pattern in self.patterns["imports"] + self.patterns["usage"]:
            if re.search(pattern, content, re.IGNORECASE):
                has_openai = True
                break
        
        if not has_openai:
            return None
        
        usage = OpenAIUsage(
            file_path=str(file_path.relative_to(self.scan_root)),
            file_type=file_path.suffix or "unknown",
            service_name=self.detect_service_name(file_path),
            api_key_source="unknown"
        )
        
        # Find imports
        for pattern in self.patterns["imports"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                usage.openai_imports.extend(matches)
        
        # Find API key references
        key_info = self.detect_api_key_in_file(file_path)
        if key_info:
            usage.api_key_hash, usage.api_key_source = key_info
        
        # Find usage patterns
        for pattern in self.patterns["usage"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                usage.usage_patterns.extend(matches)
                usage.direct_api_calls += len(matches)
        
        # Find environment variables
        env_patterns = [
            r'os\.getenv\(["\']OPENAI[^"\']+["\']',
            r'os\.environ\[["\']OPENAI[^"\']+["\']',
            r'\$OPENAI[_\w]+',
            r'OPENAI[_\w]+\s*=',
        ]
        for pattern in env_patterns:
            matches = re.findall(pattern, content)
            if matches:
                usage.env_vars.extend(matches)
        
        # Check if using tracked wrapper
        if "TrackedOpenAI" in content or "cost_tracker" in content or "get_tracker" in content:
            usage.wrapped_usage = True
        
        return usage if (usage.openai_imports or usage.usage_patterns or usage.env_vars) else None
    
    def scan_directory(self, directory: Optional[Path] = None) -> List[OpenAIUsage]:
        """Recursively scan directory for OpenAI usage"""
        if directory is None:
            directory = self.scan_root
        
        directory = Path(directory)
        if not directory.exists():
            logger.warning(f"Scan directory does not exist: {directory}")
            return []
        
        logger.info(f"🔍 Scanning {directory} for OpenAI usage...")
        
        usages = []
        scanned_files = 0
        
        for root, dirs, files in os.walk(directory):
            # Skip directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                
                # Check if we should scan this file
                if file_path.suffix not in self.scan_extensions and file_path.suffix:
                    continue
                
                scanned_files += 1
                if scanned_files % 100 == 0:
                    logger.info(f"   Scanned {scanned_files} files...")
                
                usage = self.scan_file(file_path)
                if usage:
                    usages.append(usage)
        
        logger.info(f"✅ Scan complete: {scanned_files} files scanned, {len(usages)} with OpenAI usage")
        
        return usages
    
    def save_registry(self, usages: List[OpenAIUsage]):
        """Save usage registry to file"""
        data = {
            "scan_date": str(Path(__file__).stat().st_mtime),
            "scan_root": str(self.scan_root),
            "usages": [asdict(u) for u in usages],
            "summary": {
                "total_files": len(usages),
                "services": list(set(u.service_name for u in usages)),
                "api_keys_found": len(set(u.api_key_hash for u in usages if u.api_key_hash)),
            }
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Registry saved to {self.registry_file}")
    
    def load_registry(self) -> Dict:
        """Load usage registry from file"""
        if not self.registry_file.exists():
            return None
        
        with open(self.registry_file, 'r') as f:
            return json.load(f)
    
    def scan_and_save(self):
        """Scan directory and save registry"""
        usages = self.scan_directory()
        self.save_registry(usages)
        return usages


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan for OpenAI API usage")
    parser.add_argument("--scan-root", default="~/dhruvil/storage/git", help="Root directory to scan")
    parser.add_argument("--output", help="Output file (default: logs/openai_registry.json)")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    scanner = OpenAIScanner(scan_root=args.scan_root)
    if args.output:
        scanner.registry_file = Path(args.output)
    
    usages = scanner.scan_and_save()
    
    print(f"\n{'='*80}")
    print(f"📊 SCAN SUMMARY")
    print(f"{'='*80}")
    print(f"Total files with OpenAI usage: {len(usages)}")
    print(f"\nServices found:")
    services = {}
    for usage in usages:
        if usage.service_name not in services:
            services[usage.service_name] = []
        services[usage.service_name].append(usage.file_path)
    
    for service, files in sorted(services.items()):
        print(f"  {service}: {len(files)} file(s)")
        for file in files[:3]:  # Show first 3
            print(f"    - {file}")
        if len(files) > 3:
            print(f"    ... and {len(files) - 3} more")
    
    print(f"\n{'='*80}")
    print(f"Registry saved to: {scanner.registry_file}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

