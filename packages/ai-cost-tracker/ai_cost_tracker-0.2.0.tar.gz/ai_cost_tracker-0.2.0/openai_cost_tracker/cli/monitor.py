#!/usr/bin/env python3
"""CLI for cost monitoring service"""

import sys
import os
from pathlib import Path

def main():
    """Main entry point for monitor command"""
    import argparse
    from dotenv import load_dotenv
    
    parser = argparse.ArgumentParser(description="Run OpenAI cost monitoring service")
    parser.add_argument("--config", help="Path to .env config file")
    parser.add_argument("--db-path", help="Path to cost tracking database")
    parser.add_argument("--no-scan", action="store_true", help="Skip initial scan")
    
    args = parser.parse_args()
    
    # Load environment
    if args.config:
        load_dotenv(args.config)
    else:
        # Try common locations
        for env_file in [".env", Path.home() / ".openai_cost_tracker" / ".env"]:
            if Path(env_file).exists():
                load_dotenv(env_file)
                break
    
    # Import after env is loaded
    from openai_cost_tracker.services import get_tracker, OpenAIScanner
    from openai_cost_tracker.monitor import CostMonitor
    
    # Initialize tracker with optional db_path
    if args.db_path:
        from openai_cost_tracker.services import CostTracker
        tracker = CostTracker(db_path=args.db_path)
    else:
        tracker = get_tracker()
    scanner = OpenAIScanner()
    monitor = CostMonitor(tracker=tracker, scanner=scanner)
    
    monitor.run(run_scan=not args.no_scan)

if __name__ == "__main__":
    main()

