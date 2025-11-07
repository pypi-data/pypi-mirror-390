#!/usr/bin/env python3
"""
Cost trends analysis module
"""

import boto3
from datetime import datetime, timedelta
from collections import defaultdict


def get_week_costs(ce_client, accounts, week_start, week_end):
    """
    Get costs for a specific week, grouped by service and usage type.
    
    Args:
        ce_client: boto3 Cost Explorer client
        accounts: List of account IDs
        week_start: Start date (datetime)
        week_end: End date (datetime)
    
    Returns:
        dict: {service: {usage_type: cost}}
    """
    cost_filter = {
        "And": [
            {
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": accounts
                }
            },
            {
                "Dimensions": {
                    "Key": "BILLING_ENTITY",
                    "Values": ["AWS"]
                }
            },
            {
                "Not": {
                    "Dimensions": {
                        "Key": "RECORD_TYPE",
                        "Values": ["Tax", "Support"]
                    }
                }
            }
        ]
    }
    
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': week_start.strftime('%Y-%m-%d'),
            'End': week_end.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['NetAmortizedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
        ],
        Filter=cost_filter
    )
    
    # Aggregate by service and usage type
    costs = defaultdict(lambda: defaultdict(float))
    
    for day in response['ResultsByTime']:
        for group in day.get('Groups', []):
            service = group['Keys'][0]
            usage_type = group['Keys'][1]
            cost = float(group['Metrics']['NetAmortizedCost']['Amount'])
            costs[service][usage_type] += cost
    
    return costs


def compare_weeks(prev_week_costs, curr_week_costs):
    """
    Compare two weeks and find increases/decreases at service level.
    
    Returns:
        list of dicts with service, prev_cost, curr_cost, change, pct_change
    """
    changes = []
    
    # Get all services from both weeks
    all_services = set(prev_week_costs.keys()) | set(curr_week_costs.keys())
    
    for service in all_services:
        prev_service = prev_week_costs.get(service, {})
        curr_service = curr_week_costs.get(service, {})
        
        # Sum all usage types for this service
        prev_cost = sum(prev_service.values())
        curr_cost = sum(curr_service.values())
        
        change = curr_cost - prev_cost
        pct_change = (change / prev_cost * 100) if prev_cost > 0 else (100 if curr_cost > 0 else 0)
        
        # Only include if change is significant (>$10 and >5%)
        if abs(change) > 10 and abs(pct_change) > 5:
            changes.append({
                'service': service,
                'prev_cost': prev_cost,
                'curr_cost': curr_cost,
                'change': change,
                'pct_change': pct_change
            })
    
    return changes


def analyze_trends(ce_client, accounts, num_weeks=3):
    """
    Analyze cost trends over the last N weeks.
    
    Args:
        ce_client: boto3 Cost Explorer client
        accounts: List of account IDs
        num_weeks: Number of weeks to analyze (default: 3)
    
    Returns:
        dict with weekly comparisons
    """
    today = datetime.now()
    
    # Calculate week boundaries (Monday to Sunday)
    # Go back to most recent Sunday
    days_since_sunday = (today.weekday() + 1) % 7
    most_recent_sunday = today - timedelta(days=days_since_sunday)
    
    weeks = []
    for i in range(num_weeks):
        week_end = most_recent_sunday - timedelta(weeks=i)
        week_start = week_end - timedelta(days=7)
        weeks.append({
            'start': week_start,
            'end': week_end,
            'label': f"Week of {week_start.strftime('%b %d')}"
        })
    
    # Reverse so oldest is first
    weeks.reverse()
    
    # Get costs for each week
    weekly_costs = []
    for week in weeks:
        costs = get_week_costs(ce_client, accounts, week['start'], week['end'])
        weekly_costs.append({
            'week': week,
            'costs': costs
        })
    
    # Compare consecutive weeks (week-over-week)
    wow_comparisons = []
    for i in range(1, len(weekly_costs)):
        prev = weekly_costs[i-1]
        curr = weekly_costs[i]
        
        changes = compare_weeks(prev['costs'], curr['costs'])
        
        # Sort by absolute change
        changes.sort(key=lambda x: abs(x['change']), reverse=True)
        increases = [c for c in changes if c['change'] > 0][:10]
        decreases = [c for c in changes if c['change'] < 0][:10]
        
        wow_comparisons.append({
            'prev_week': prev['week'],
            'curr_week': curr['week'],
            'increases': increases,
            'decreases': decreases,
            'total_increase': sum(c['change'] for c in increases),
            'total_decrease': sum(c['change'] for c in decreases)
        })
    
    # Compare to 30 days ago (T-30)
    t30_comparisons = []
    for i in range(len(weekly_costs)):
        curr = weekly_costs[i]
        # Find week from ~30 days ago (4-5 weeks back)
        baseline_idx = i - 4 if i >= 4 else None
        
        if baseline_idx is not None and baseline_idx >= 0:
            baseline = weekly_costs[baseline_idx]
            
            changes = compare_weeks(baseline['costs'], curr['costs'])
            
            # Sort by absolute change
            changes.sort(key=lambda x: abs(x['change']), reverse=True)
            increases = [c for c in changes if c['change'] > 0][:10]
            decreases = [c for c in changes if c['change'] < 0][:10]
            
            t30_comparisons.append({
                'baseline_week': baseline['week'],
                'curr_week': curr['week'],
                'increases': increases,
                'decreases': decreases,
                'total_increase': sum(c['change'] for c in increases),
                'total_decrease': sum(c['change'] for c in decreases)
            })
    
    # Reverse so most recent is first
    wow_comparisons.reverse()
    t30_comparisons.reverse()
    
    return {
        'weeks': weeks,
        'wow_comparisons': wow_comparisons,
        't30_comparisons': t30_comparisons
    }


def format_trends_markdown(trends_data):
    """
    Format trends data as markdown.
    
    Returns:
        str: Markdown formatted report
    """
    lines = []
    lines.append("# AWS Cost Trends Report (Service Level)")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append("This report shows two types of comparisons:")
    lines.append("")
    lines.append("1. **Week-over-Week (WoW)**: Compares each week to the previous week")
    lines.append("   - Good for catching immediate changes and spikes")
    lines.append("   - Shows short-term volatility")
    lines.append("")
    lines.append("2. **Trailing 30-Day (T-30)**: Compares each week to the same week 4 weeks ago")
    lines.append("   - Filters out weekly noise")
    lines.append("   - Shows sustained trends and real cost changes")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# Week-over-Week Changes")
    lines.append("")
    
    for comparison in trends_data['wow_comparisons']:
        prev_week = comparison['prev_week']
        curr_week = comparison['curr_week']
        
        lines.append(f"## {prev_week['label']} → {curr_week['label']}")
        lines.append("")
        
        # Top increases
        if comparison['increases']:
            lines.append("### 🔴 Top 10 Increases")
            lines.append("")
            lines.append("| Service | Previous | Current | Change | % |")
            lines.append("|---------|----------|---------|--------|---|")
            
            for item in comparison['increases']:
                service = item['service'][:60]
                prev = f"${item['prev_cost']:,.2f}"
                curr = f"${item['curr_cost']:,.2f}"
                change = f"${item['change']:,.2f}"
                pct = f"{item['pct_change']:+.1f}%"
                
                lines.append(f"| {service} | {prev} | {curr} | {change} | {pct} |")
            
            # Add total row
            total_increase = comparison.get('total_increase', 0)
            lines.append(f"| **TOTAL** | | | **${total_increase:,.2f}** | |")
            
            lines.append("")
        
        # Top decreases
        if comparison['decreases']:
            lines.append("### 🟢 Top 10 Decreases")
            lines.append("")
            lines.append("| Service | Previous | Current | Change | % |")
            lines.append("|---------|----------|---------|--------|---|")
            
            for item in comparison['decreases']:
                service = item['service'][:60]
                prev = f"${item['prev_cost']:,.2f}"
                curr = f"${item['curr_cost']:,.2f}"
                change = f"${item['change']:,.2f}"
                pct = f"{item['pct_change']:+.1f}%"
                
                lines.append(f"| {service} | {prev} | {curr} | {change} | {pct} |")
            
            # Add total row
            total_decrease = comparison.get('total_decrease', 0)
            lines.append(f"| **TOTAL** | | | **${total_decrease:,.2f}** | |")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Add T-30 comparisons section
    lines.append("")
    lines.append("# Trailing 30-Day Comparisons (T-30)")
    lines.append("")
    
    for comparison in trends_data['t30_comparisons']:
        baseline_week = comparison['baseline_week']
        curr_week = comparison['curr_week']
        
        lines.append(f"## {curr_week['label']} vs {baseline_week['label']} (30 days ago)")
        lines.append("")
        
        # Top increases
        if comparison['increases']:
            lines.append("### 🔴 Top 10 Increases (vs 30 days ago)")
            lines.append("")
            lines.append("| Service | 30 Days Ago | Current | Change | % |")
            lines.append("|---------|-------------|---------|--------|---|")
            
            for item in comparison['increases']:
                service = item['service'][:60]
                prev = f"${item['prev_cost']:,.2f}"
                curr = f"${item['curr_cost']:,.2f}"
                change = f"${item['change']:,.2f}"
                pct = f"{item['pct_change']:+.1f}%"
                
                lines.append(f"| {service} | {prev} | {curr} | {change} | {pct} |")
            
            # Add total row
            total_increase = comparison.get('total_increase', 0)
            lines.append(f"| **TOTAL** | | | **${total_increase:,.2f}** | |")
            
            lines.append("")
        
        # Top decreases
        if comparison['decreases']:
            lines.append("### 🟢 Top 10 Decreases (vs 30 days ago)")
            lines.append("")
            lines.append("| Service | 30 Days Ago | Current | Change | % |")
            lines.append("|---------|-------------|---------|--------|---|")
            
            for item in comparison['decreases']:
                service = item['service'][:60]
                prev = f"${item['prev_cost']:,.2f}"
                curr = f"${item['curr_cost']:,.2f}"
                change = f"${item['change']:,.2f}"
                pct = f"{item['pct_change']:+.1f}%"
                
                lines.append(f"| {service} | {prev} | {curr} | {change} | {pct} |")
            
            # Add total row
            total_decrease = comparison.get('total_decrease', 0)
            lines.append(f"| **TOTAL** | | | **${total_decrease:,.2f}** | |")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)
