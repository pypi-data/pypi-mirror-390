#!/usr/bin/env python3
"""
OpenAI Cost Viewer - View and analyze API usage and costs
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from openai_cost_tracker.services import get_tracker

def format_currency(amount: float) -> str:
    """Format currency amount"""
    return f"${amount:,.4f}"

def print_summary(summary: dict):
    """Print usage summary"""
    print("=" * 80)
    print("💰 OPENAI API COST SUMMARY")
    print("=" * 80)
    print()
    
    print(f"📊 Total Cost: {format_currency(summary['total_cost_usd'])}")
    print(f"📞 Total API Calls: {summary['total_calls']:,}")
    print()
    
    if summary['total_calls'] > 0:
        avg_cost = summary['total_cost_usd'] / summary['total_calls']
        print(f"📈 Average Cost per Call: {format_currency(avg_cost)}")
        print()
    
    # By Service
    if summary['by_service']:
        print("📋 COSTS BY SERVICE:")
        print("-" * 80)
        for service, data in sorted(summary['by_service'].items(), key=lambda x: x[1]['cost'], reverse=True):
            percentage = (data['cost'] / summary['total_cost_usd'] * 100) if summary['total_cost_usd'] > 0 else 0
            print(f"  {service:40s} {format_currency(data['cost']):>15s} ({data['calls']:>4d} calls, {percentage:>5.1f}%)")
        print()
    
    # By API Type
    if summary['by_api_type']:
        print("📋 COSTS BY API TYPE:")
        print("-" * 80)
        for api_type, data in sorted(summary['by_api_type'].items(), key=lambda x: x[1]['cost'], reverse=True):
            percentage = (data['cost'] / summary['total_cost_usd'] * 100) if summary['total_cost_usd'] > 0 else 0
            print(f"  {api_type:40s} {format_currency(data['cost']):>15s} ({data['calls']:>4d} calls, {percentage:>5.1f}%)")
        print()
    
    # By Model
    if summary['by_model']:
        print("📋 COSTS BY MODEL:")
        print("-" * 80)
        for model, data in sorted(summary['by_model'].items(), key=lambda x: x[1]['cost'], reverse=True):
            percentage = (data['cost'] / summary['total_cost_usd'] * 100) if summary['total_cost_usd'] > 0 else 0
            print(f"  {model:40s} {format_currency(data['cost']):>15s} ({data['calls']:>4d} calls, {percentage:>5.1f}%)")
        print()

def print_recent_calls(records: list, limit: int = 20):
    """Print recent API calls"""
    print("=" * 80)
    print(f"📜 RECENT API CALLS (Last {limit})")
    print("=" * 80)
    print()
    
    for record in records[:limit]:
        timestamp = datetime.fromisoformat(record['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        success_icon = "✅" if record['success'] else "❌"
        cost_str = format_currency(record['cost_usd'])
        
        print(f"{success_icon} [{timestamp}] {record['service_name']:30s}")
        print(f"    Type: {record['api_type']:10s} | Model: {record['model']:20s} | Operation: {record['operation']}")
        print(f"    Cost: {cost_str}")
        
        if record['video_seconds']:
            print(f"    Video: {record['video_seconds']}s")
        if record['image_size']:
            print(f"    Image: {record['image_size']} ({record['image_quality'] or 'standard'})")
        if record['tokens_input'] or record['tokens_output']:
            print(f"    Tokens: In={record['tokens_input'] or 0}, Out={record['tokens_output'] or 0}")
        if record['error_message']:
            print(f"    Error: {record['error_message'][:100]}")
        if record['api_key_hash']:
            print(f"    API Key: {record['api_key_hash']}")
        print()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="View OpenAI API costs and usage")
    parser.add_argument("--days", type=int, default=None, help="Number of days to look back")
    parser.add_argument("--service", type=str, default=None, help="Filter by service name")
    parser.add_argument("--api-key", type=str, default=None, help="Filter by API key hash")
    parser.add_argument("--recent", type=int, default=20, help="Show N recent calls")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--export", type=str, help="Export to JSON file")
    
    args = parser.parse_args()
    
    tracker = get_tracker()
    
    # Calculate date range
    start_date = None
    end_date = None
    if args.days:
        end_date = datetime.utcnow().isoformat()
        start_date = (datetime.utcnow() - timedelta(days=args.days)).isoformat()
    
    # Get summary
    summary = tracker.get_usage_summary(
        start_date=start_date,
        end_date=end_date,
        service_name=args.service,
        api_key_hash=args.api_key
    )
    
    # Export if requested
    if args.export:
        with open(args.export, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"✅ Exported to {args.export}")
        return
    
    # JSON output
    if args.json:
        print(json.dumps(summary, indent=2, default=str))
        return
    
    # Print summary
    print_summary(summary)
    
    # Print recent calls
    if summary['records']:
        print_recent_calls(summary['records'], limit=args.recent)

if __name__ == "__main__":
    main()

