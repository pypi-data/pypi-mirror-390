"""
Drill-down cost analysis module.
Allows filtering by service, account, and usage type for detailed cost investigation.
"""
from datetime import datetime, timedelta
from collections import defaultdict


def get_filtered_costs(ce_client, accounts, time_start, time_end, granularity='DAILY', 
                       service_filter=None, account_filter=None, usage_type_filter=None):
    """
    Get costs with optional filters, grouped by the next level of detail.
    
    Args:
        ce_client: boto3 Cost Explorer client
        accounts: List of account IDs
        time_start: datetime for start
        time_end: datetime for end
        granularity: 'WEEKLY' or 'MONTHLY'
        service_filter: Optional service name to filter
        account_filter: Optional account ID to filter
        usage_type_filter: Optional usage type to filter
    
    Returns:
        dict: {dimension_value: total_cost}
    """
    # Build filter
    filters = []
    
    # Account filter (either from account_filter or all accounts)
    if account_filter:
        filters.append({
            "Dimensions": {
                "Key": "LINKED_ACCOUNT",
                "Values": [account_filter]
            }
        })
    else:
        filters.append({
            "Dimensions": {
                "Key": "LINKED_ACCOUNT",
                "Values": accounts
            }
        })
    
    # Service filter
    if service_filter:
        filters.append({
            "Dimensions": {
                "Key": "SERVICE",
                "Values": [service_filter]
            }
        })
    
    # Usage type filter
    if usage_type_filter:
        filters.append({
            "Dimensions": {
                "Key": "USAGE_TYPE",
                "Values": [usage_type_filter]
            }
        })
    
    # Determine what to group by (next level of detail)
    if usage_type_filter:
        # Already at usage type level, group by region
        group_by_key = 'REGION'
    elif service_filter and account_filter:
        # Have service and account, show usage types
        group_by_key = 'USAGE_TYPE'
    elif service_filter:
        # Have service, show accounts
        group_by_key = 'LINKED_ACCOUNT'
    elif account_filter:
        # Have account, show services
        group_by_key = 'SERVICE'
    else:
        # No filters, show services (same as trends)
        group_by_key = 'SERVICE'
    
    # Build final filter
    if len(filters) > 1:
        final_filter = {"And": filters}
    else:
        final_filter = filters[0]
    
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': time_start.strftime('%Y-%m-%d'),
            'End': time_end.strftime('%Y-%m-%d')
        },
        Granularity=granularity,
        Filter=final_filter,
        Metrics=['NetAmortizedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': group_by_key}
        ]
    )
    
    costs = defaultdict(float)
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            dimension_value = group['Keys'][0]
            cost = float(group['Metrics']['NetAmortizedCost']['Amount'])
            costs[dimension_value] += cost
    
    return costs, group_by_key


def compare_periods(prev_costs, curr_costs):
    """
    Compare two periods and find increases/decreases.
    
    Returns:
        list of dicts with dimension, prev_cost, curr_cost, change, pct_change
    """
    changes = []
    
    # Get all dimensions from both periods
    all_dimensions = set(prev_costs.keys()) | set(curr_costs.keys())
    
    for dimension in all_dimensions:
        prev_cost = prev_costs.get(dimension, 0)
        curr_cost = curr_costs.get(dimension, 0)
        
        change = curr_cost - prev_cost
        pct_change = (change / prev_cost * 100) if prev_cost > 0 else (100 if curr_cost > 0 else 0)
        
        # Only include if change is significant (>$10 and >5%)
        if abs(change) > 10 and abs(pct_change) > 5:
            changes.append({
                'dimension': dimension,
                'prev_cost': prev_cost,
                'curr_cost': curr_cost,
                'change': change,
                'pct_change': pct_change
            })
    
    return changes


def analyze_drill_down(ce_client, accounts, num_weeks=4, service_filter=None, 
                       account_filter=None, usage_type_filter=None):
    """
    Analyze cost trends with drill-down filters.
    
    Args:
        ce_client: boto3 Cost Explorer client
        accounts: List of account IDs
        num_weeks: Number of weeks to analyze (default: 4)
        service_filter: Optional service name to filter
        account_filter: Optional account ID to filter
        usage_type_filter: Optional usage type to filter
    
    Returns:
        dict with weekly comparisons and metadata
    """
    today = datetime.now()
    
    # Calculate week boundaries (Monday to Sunday)
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
    group_by_key = None
    for week in weeks:
        costs, group_by_key = get_filtered_costs(
            ce_client, accounts, week['start'], week['end'],
            service_filter=service_filter,
            account_filter=account_filter,
            usage_type_filter=usage_type_filter
        )
        weekly_costs.append({
            'week': week,
            'costs': costs
        })
    
    # Compare consecutive weeks
    comparisons = []
    for i in range(1, len(weekly_costs)):
        prev = weekly_costs[i-1]
        curr = weekly_costs[i]
        
        changes = compare_periods(prev['costs'], curr['costs'])
        
        # Sort by absolute change
        changes.sort(key=lambda x: abs(x['change']), reverse=True)
        increases = [c for c in changes if c['change'] > 0][:10]
        decreases = [c for c in changes if c['change'] < 0][:10]
        
        comparisons.append({
            'prev_week': prev['week'],
            'curr_week': curr['week'],
            'increases': increases,
            'decreases': decreases,
            'total_increase': sum(c['change'] for c in increases),
            'total_decrease': sum(c['change'] for c in decreases)
        })
    
    # Reverse so most recent is first
    comparisons.reverse()
    
    return {
        'weeks': weeks,
        'comparisons': comparisons,
        'group_by': group_by_key,
        'filters': {
            'service': service_filter,
            'account': account_filter,
            'usage_type': usage_type_filter
        }
    }


def format_drill_down_markdown(drill_data):
    """
    Format drill-down data as markdown.
    
    Returns:
        str: Markdown formatted report
    """
    lines = []
    lines.append("# AWS Cost Drill-Down Report")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Show active filters
    filters = drill_data['filters']
    lines.append("## Filters Applied")
    lines.append("")
    if filters['service']:
        lines.append(f"- **Service:** {filters['service']}")
    if filters['account']:
        lines.append(f"- **Account:** {filters['account']}")
    if filters['usage_type']:
        lines.append(f"- **Usage Type:** {filters['usage_type']}")
    if not any(filters.values()):
        lines.append("- No filters (showing all services)")
    lines.append("")
    
    # Show what dimension we're grouping by
    group_by = drill_data['group_by']
    dimension_label = {
        'SERVICE': 'Service',
        'LINKED_ACCOUNT': 'Account',
        'USAGE_TYPE': 'Usage Type',
        'REGION': 'Region'
    }.get(group_by, group_by)
    
    lines.append(f"## Grouped By: {dimension_label}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for comparison in drill_data['comparisons']:
        prev_week = comparison['prev_week']
        curr_week = comparison['curr_week']
        
        lines.append(f"## {prev_week['label']} → {curr_week['label']}")
        lines.append("")
        
        # Top increases
        if comparison['increases']:
            lines.append("### 🔴 Top 10 Increases")
            lines.append("")
            lines.append(f"| {dimension_label} | Previous | Current | Change | % |")
            lines.append("|---------|----------|---------|--------|---|")
            
            for item in comparison['increases']:
                dimension = item['dimension'][:60]
                prev = f"${item['prev_cost']:,.2f}"
                curr = f"${item['curr_cost']:,.2f}"
                change = f"${item['change']:,.2f}"
                pct = f"{item['pct_change']:+.1f}%"
                
                lines.append(f"| {dimension} | {prev} | {curr} | {change} | {pct} |")
            
            # Add total row
            total_increase = comparison.get('total_increase', 0)
            lines.append(f"| **TOTAL** | | | **${total_increase:,.2f}** | |")
            
            lines.append("")
        
        # Top decreases
        if comparison['decreases']:
            lines.append("### 🟢 Top 10 Decreases")
            lines.append("")
            lines.append(f"| {dimension_label} | Previous | Current | Change | % |")
            lines.append("|---------|----------|---------|--------|---|")
            
            for item in comparison['decreases']:
                dimension = item['dimension'][:60]
                prev = f"${item['prev_cost']:,.2f}"
                curr = f"${item['curr_cost']:,.2f}"
                change = f"${item['change']:,.2f}"
                pct = f"{item['pct_change']:+.1f}%"
                
                lines.append(f"| {dimension} | {prev} | {curr} | {change} | {pct} |")
            
            # Add total row
            total_decrease = comparison.get('total_decrease', 0)
            lines.append(f"| **TOTAL** | | | **${total_decrease:,.2f}** | |")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)
