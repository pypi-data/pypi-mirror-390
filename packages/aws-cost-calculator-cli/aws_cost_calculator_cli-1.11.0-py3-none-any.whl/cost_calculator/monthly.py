"""
Monthly cost trend analysis module.
Analyzes month-over-month cost changes at the service level.
"""
from datetime import datetime, timedelta
from collections import defaultdict


def get_month_costs(ce_client, accounts, month_start, month_end):
    """
    Get costs for a specific month grouped by service.
    
    Args:
        ce_client: boto3 Cost Explorer client
        accounts: List of account IDs
        month_start: datetime for start of month
        month_end: datetime for end of month
    
    Returns:
        dict: {service: total_cost}
    """
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': month_start.strftime('%Y-%m-%d'),
            'End': month_end.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Filter={
            "Dimensions": {
                "Key": "LINKED_ACCOUNT",
                "Values": accounts
            }
        },
        Metrics=['NetAmortizedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'}
        ]
    )
    
    costs = defaultdict(float)
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['NetAmortizedCost']['Amount'])
            costs[service] += cost
    
    return costs


def compare_months(prev_month_costs, curr_month_costs):
    """
    Compare two months and find increases/decreases at service level.
    
    Returns:
        list of dicts with service, prev_cost, curr_cost, change, pct_change
    """
    changes = []
    
    # Get all services from both months
    all_services = set(prev_month_costs.keys()) | set(curr_month_costs.keys())
    
    for service in all_services:
        prev_cost = prev_month_costs.get(service, 0)
        curr_cost = curr_month_costs.get(service, 0)
        
        change = curr_cost - prev_cost
        pct_change = (change / prev_cost * 100) if prev_cost > 0 else (100 if curr_cost > 0 else 0)
        
        # Only include if change is significant (>$50 and >5%)
        if abs(change) > 50 and abs(pct_change) > 5:
            changes.append({
                'service': service,
                'prev_cost': prev_cost,
                'curr_cost': curr_cost,
                'change': change,
                'pct_change': pct_change
            })
    
    return changes


def analyze_monthly_trends(ce_client, accounts, num_months=6):
    """
    Analyze cost trends over the last N months.
    
    Args:
        ce_client: boto3 Cost Explorer client
        accounts: List of account IDs
        num_months: Number of months to analyze (default: 6)
    
    Returns:
        dict with monthly comparisons
    """
    today = datetime.now()
    
    # Calculate month boundaries
    months = []
    for i in range(num_months):
        # Go back i months from today
        if today.month - i <= 0:
            year = today.year - 1
            month = 12 + (today.month - i)
        else:
            year = today.year
            month = today.month - i
        
        # First day of month
        month_start = datetime(year, month, 1)
        
        # First day of next month
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)
        
        months.append({
            'start': month_start,
            'end': month_end,
            'label': month_start.strftime('%B %Y')
        })
    
    # Reverse so oldest is first
    months.reverse()
    
    # Get costs for each month
    monthly_costs = []
    for month in months:
        costs = get_month_costs(ce_client, accounts, month['start'], month['end'])
        monthly_costs.append({
            'month': month,
            'costs': costs
        })
    
    # Compare consecutive months
    comparisons = []
    for i in range(1, len(monthly_costs)):
        prev = monthly_costs[i-1]
        curr = monthly_costs[i]
        
        changes = compare_months(prev['costs'], curr['costs'])
        
        # Sort by absolute change
        changes.sort(key=lambda x: abs(x['change']), reverse=True)
        increases = [c for c in changes if c['change'] > 0][:10]
        decreases = [c for c in changes if c['change'] < 0][:10]
        
        comparisons.append({
            'prev_month': prev['month'],
            'curr_month': curr['month'],
            'increases': increases,
            'decreases': decreases,
            'total_increase': sum(c['change'] for c in increases),
            'total_decrease': sum(c['change'] for c in decreases)
        })
    
    # Reverse so most recent is first
    comparisons.reverse()
    
    return {
        'months': months,
        'comparisons': comparisons
    }


def format_monthly_markdown(monthly_data):
    """
    Format monthly trends data as markdown.
    
    Returns:
        str: Markdown formatted report
    """
    lines = []
    lines.append("# AWS Monthly Cost Trends Report (Service Level)")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append("This report shows month-over-month cost changes at the service level:")
    lines.append("")
    lines.append("- Compares consecutive calendar months")
    lines.append("- Shows total cost per service (aggregated across all usage types)")
    lines.append("- Filters out noise (>$50 and >5% change)")
    lines.append("- Most recent comparisons first")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for comparison in monthly_data['comparisons']:
        prev_month = comparison['prev_month']
        curr_month = comparison['curr_month']
        
        lines.append(f"## {prev_month['label']} → {curr_month['label']}")
        lines.append("")
        
        # Top increases
        if comparison['increases']:
            lines.append("### 🔴 Top 10 Increases")
            lines.append("")
            lines.append("| Service | Previous Month | Current Month | Change | % |")
            lines.append("|---------|----------------|---------------|--------|---|")
            
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
            lines.append("| Service | Previous Month | Current Month | Change | % |")
            lines.append("|---------|----------------|---------------|--------|---|")
            
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
