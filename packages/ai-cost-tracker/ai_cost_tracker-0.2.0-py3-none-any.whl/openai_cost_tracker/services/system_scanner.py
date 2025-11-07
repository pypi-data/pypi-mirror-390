#!/usr/bin/env python3
"""
System-Wide AI API Scanner
Scans entire system for AI provider API keys and usage across all file types
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass

from .universal_tracker import SUPPORTED_PROVIDERS


@dataclass
class SystemAIUsage:
    """System-wide AI usage detection"""
    file_path: str
    provider: str
    language: Optional[str]
    api_key_pattern: str
    api_key_hash: Optional[str]
    endpoints_found: List[str]
    usage_count: int


class SystemWideScanner:
    """Scans entire system for AI API usage"""
    
    def __init__(self, scan_roots: Optional[List[str]] = None):
        """Initialize scanner"""
        if scan_roots is None:
            # Default to common locations
            self.scan_roots = [
                str(Path.home()),
                "/usr/local",
                "/opt",
            ]
            # Exclude system directories
            self.skip_dirs = {
                "__pycache__", "node_modules", ".git", ".venv", "venv",
                "env", ".env", "dist", "build", ".pytest_cache",
                "logs", ".idea", ".vscode", ".DS_Store",
                "Library", "System", "proc", "sys", "dev"
            }
        else:
            self.scan_roots = scan_roots
            self.skip_dirs = set()
        
        # File extensions to scan
        self.scan_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".tsx",
            ".java", ".go", ".rs", ".rb", ".php",
            ".sh", ".bash", ".zsh",
            ".yaml", ".yml", ".json", ".env", ".config",
            ".service", ".conf", ".ini",
        }
    
    def hash_api_key(self, key: str) -> str:
        """Hash API key"""
        import hashlib
        if not key:
            return None
        key = key.strip().strip('"').strip("'")
        hash_obj = hashlib.sha256(key.encode())
        return hash_obj.hexdigest()[:16]
    
    def detect_provider_from_key(self, key: str) -> Optional[str]:
        """Detect provider from API key pattern"""
        for provider, info in SUPPORTED_PROVIDERS.items():
            for pattern in info["api_key_patterns"]:
                if re.search(pattern, key, re.IGNORECASE):
                    return provider
        return None
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".sh": "bash",
            ".bash": "bash",
        }
        return lang_map.get(ext)
    
    def scan_file(self, file_path: Path) -> Optional[SystemAIUsage]:
        """Scan a single file for AI API usage"""
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(errors='ignore')
        except:
            return None
        
        findings = {}
        
        # Check each provider's patterns
        for provider, info in SUPPORTED_PROVIDERS.items():
            matches = []
            
            # Check API key patterns
            for pattern in info["api_key_patterns"]:
                key_matches = re.findall(pattern, content, re.IGNORECASE)
                matches.extend(key_matches)
            
            # Check endpoint patterns
            for endpoint in info["endpoints"]:
                if endpoint in content:
                    matches.append(f"endpoint:{endpoint}")
            
            if matches:
                # Extract actual API key if found
                api_key = None
                api_key_hash = None
                for match in matches:
                    if match.startswith("sk-") or match.startswith("pplx-") or match.startswith("xai-") or match.startswith("AIza"):
                        api_key = match
                        api_key_hash = self.hash_api_key(match)
                        break
                
                findings[provider] = {
                    "api_key_pattern": matches[0] if matches else "found",
                    "api_key_hash": api_key_hash,
                    "endpoints": [m.replace("endpoint:", "") for m in matches if m.startswith("endpoint:")],
                    "count": len([m for m in matches if not m.startswith("endpoint:")])
                }
        
        if not findings:
            return None
        
        # Return first finding (or could return all)
        provider = list(findings.keys())[0]
        finding = findings[provider]
        
        return SystemAIUsage(
            file_path=str(file_path),
            provider=provider,
            language=self.detect_language(file_path),
            api_key_pattern=finding["api_key_pattern"],
            api_key_hash=finding["api_key_hash"],
            endpoints_found=finding["endpoints"],
            usage_count=finding["count"]
        )
    
    def scan_directory(self, directory: Path, max_depth: int = 10, current_depth: int = 0) -> List[SystemAIUsage]:
        """Recursively scan directory"""
        if current_depth > max_depth:
            return []
        
        usages = []
        
        try:
            for item in directory.iterdir():
                # Skip directories
                if item.is_dir():
                    if item.name in self.skip_dirs:
                        continue
                    if item.name.startswith('.'):
                        continue
                    # Recursive scan
                    usages.extend(self.scan_directory(item, max_depth, current_depth + 1))
                
                # Scan files
                elif item.is_file():
                    if item.suffix in self.scan_extensions or not item.suffix:
                        usage = self.scan_file(item)
                        if usage:
                            usages.append(usage)
        except PermissionError:
            pass
        except Exception:
            pass
        
        return usages
    
    def scan_system(self) -> Dict[str, Any]:
        """Scan entire system"""
        all_usages = []
        
        for root in self.scan_roots:
            root_path = Path(root)
            if root_path.exists():
                print(f"🔍 Scanning {root_path}...")
                usages = self.scan_directory(root_path, max_depth=5)
                all_usages.extend(usages)
                print(f"   Found {len(usages)} files with AI usage")
        
        # Summarize
        by_provider = {}
        by_language = {}
        api_keys_found = set()
        
        for usage in all_usages:
            provider = usage.provider
            language = usage.language or "unknown"
            
            by_provider[provider] = by_provider.get(provider, 0) + 1
            by_language[language] = by_language.get(language, 0) + 1
            
            if usage.api_key_hash:
                api_keys_found.add(usage.api_key_hash)
        
        return {
            "total_files": len(all_usages),
            "by_provider": by_provider,
            "by_language": by_language,
            "unique_api_keys": len(api_keys_found),
            "usages": [{
                "file": u.file_path,
                "provider": u.provider,
                "language": u.language,
                "api_key_hash": u.api_key_hash,
                "usage_count": u.usage_count
            } for u in all_usages]
        }


if __name__ == "__main__":
    import sys
    
    scanner = SystemWideScanner()
    
    if len(sys.argv) > 1:
        # Custom scan roots
        scanner = SystemWideScanner(scan_roots=sys.argv[1:])
    
    print("🔍 Starting system-wide AI API scan...")
    print("⚠️  This may take a while and scan many files...")
    
    results = scanner.scan_system()
    
    print("\n" + "="*80)
    print("📊 SCAN RESULTS")
    print("="*80)
    print(f"Total files with AI usage: {results['total_files']}")
    print(f"Unique API keys found: {results['unique_api_keys']}")
    print("\nBy Provider:")
    for provider, count in sorted(results['by_provider'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {provider}: {count} files")
    print("\nBy Language:")
    for lang, count in sorted(results['by_language'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {lang}: {count} files")
    
    # Save results
    output_file = Path.home() / ".ai_cost_tracker" / "system_scan.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")

