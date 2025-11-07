#!/usr/bin/env python3
"""CLI for scanning OpenAI usage"""

import sys
from pathlib import Path
from openai_cost_tracker.services import OpenAIScanner

def main():
    """Main entry point for scan command"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan for OpenAI API usage")
    parser.add_argument("--scan-root", default=None, help="Root directory to scan (default: current directory)")
    parser.add_argument("--output", help="Output file (default: ~/.openai_cost_tracker/openai_registry.json)")
    
    args = parser.parse_args()
    
    scanner = OpenAIScanner(scan_root=args.scan_root)
    if args.output:
        scanner.registry_file = Path(args.output)
    
    print(f"🔍 Scanning {scanner.scan_root} for OpenAI usage...")
    usages = scanner.scan_and_save()
    
    print(f"\n{'='*80}")
    print(f"📊 SCAN SUMMARY")
    print(f"{'='*80}")
    print(f"Total files with OpenAI usage: {len(usages)}")
    
    services = {}
    api_keys = set()
    for usage in usages:
        if usage.service_name not in services:
            services[usage.service_name] = []
        services[usage.service_name].append(usage.file_path)
        if usage.api_key_hash:
            api_keys.add(usage.api_key_hash)
    
    print(f"\nServices found ({len(services)}):")
    for service, files in sorted(services.items()):
        print(f"  {service}: {len(files)} file(s)")
        for file in files[:2]:
            print(f"    - {file}")
        if len(files) > 2:
            print(f"    ... and {len(files) - 2} more")
    
    if api_keys:
        print(f"\nAPI keys detected: {len(api_keys)}")
    
    print(f"\n{'='*80}")
    print(f"Registry saved to: {scanner.registry_file}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

