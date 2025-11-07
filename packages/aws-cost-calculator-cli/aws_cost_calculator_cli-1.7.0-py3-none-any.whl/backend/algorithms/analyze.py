"""
Analysis algorithm using pandas for aggregations.
Reuses existing algorithms and adds pandas-based analytics.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from algorithms.trends import analyze_trends
from algorithms.drill import analyze_drill_down


def analyze_aggregated(ce_client, accounts, weeks=12, analysis_type='summary'):
    """
    Perform pandas-based analysis on cost data.
    
    Args:
        ce_client: boto3 Cost Explorer client
        accounts: List of account IDs
        weeks: Number of weeks to analyze
        analysis_type: 'summary', 'volatility', 'trends', 'multi_group'
    
    Returns:
        dict with analysis results
    """
    # Get raw data from trends
    trends_data = analyze_trends(ce_client, accounts, weeks)
    
    # Convert to pandas DataFrame
    rows = []
    for comp in trends_data['wow_comparisons']:
        week_label = comp['curr_week']['label']
        for item in comp['increases'] + comp['decreases']:
            rows.append({
                'week': week_label,
                'service': item['service'],
                'prev_cost': item['prev_cost'],
                'curr_cost': item['curr_cost'],
                'change': item['change'],
                'pct_change': item['pct_change']
            })
    
    df = pd.DataFrame(rows)
    
    if df.empty:
        return {'error': 'No data available'}
    
    # Perform requested analysis
    if analysis_type == 'summary':
        return _analyze_summary(df, weeks)
    elif analysis_type == 'volatility':
        return _analyze_volatility(df)
    elif analysis_type == 'trends':
        return _detect_trends(df)
    elif analysis_type == 'multi_group':
        return _multi_group_analysis(ce_client, accounts, weeks)
    else:
        return {'error': f'Unknown analysis type: {analysis_type}'}


def _analyze_summary(df, weeks):
    """Aggregate summary statistics across all weeks."""
    # Group by service and aggregate
    summary = df.groupby('service').agg({
        'change': ['sum', 'mean', 'std', 'min', 'max', 'count'],
        'curr_cost': ['sum', 'mean']
    }).round(2)
    
    # Flatten column names
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    
    # Calculate coefficient of variation
    summary['volatility'] = (summary['change_std'] / summary['change_mean'].abs()).fillna(0).round(3)
    
    # Sort by total change
    summary = summary.sort_values('change_sum', ascending=False)
    
    # Convert to dict
    results = summary.to_dict('records')
    
    # Add percentiles
    percentiles = df.groupby('service')['change'].sum().quantile([0.5, 0.9, 0.99]).to_dict()
    
    return {
        'analysis_type': 'summary',
        'weeks_analyzed': weeks,
        'total_services': len(results),
        'services': results[:50],  # Top 50
        'percentiles': {
            'p50': round(percentiles.get(0.5, 0), 2),
            'p90': round(percentiles.get(0.9, 0), 2),
            'p99': round(percentiles.get(0.99, 0), 2)
        }
    }


def _analyze_volatility(df):
    """Identify services with high cost volatility."""
    # Calculate volatility metrics
    volatility = df.groupby('service').agg({
        'change': ['mean', 'std', 'count']
    })
    
    volatility.columns = ['mean_change', 'std_change', 'weeks']
    volatility['coefficient_of_variation'] = (volatility['std_change'] / volatility['mean_change'].abs()).fillna(0)
    
    # Only services that appear in at least 3 weeks
    volatility = volatility[volatility['weeks'] >= 3]
    
    # Sort by CV
    volatility = volatility.sort_values('coefficient_of_variation', ascending=False)
    volatility = volatility.reset_index()
    
    # Identify outliers (z-score > 2)
    df['z_score'] = df.groupby('service')['change'].transform(
        lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
    )
    outliers = df[df['z_score'].abs() > 2][['week', 'service', 'change', 'z_score']].to_dict('records')
    
    return {
        'analysis_type': 'volatility',
        'high_volatility_services': volatility.head(20).to_dict('records'),
        'outliers': outliers[:20]
    }


def _detect_trends(df):
    """Detect services with consistent increasing/decreasing trends."""
    # Calculate trend for each service
    trends = []
    
    for service in df['service'].unique():
        service_df = df[df['service'] == service].sort_values('week')
        
        if len(service_df) < 3:
            continue
        
        # Calculate linear regression slope
        x = np.arange(len(service_df))
        y = service_df['change'].values
        
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            avg_change = service_df['change'].mean()
            
            # Classify trend
            if slope > avg_change * 0.1:  # Increasing by >10% on average
                trend_type = 'increasing'
            elif slope < -avg_change * 0.1:  # Decreasing by >10%
                trend_type = 'decreasing'
            else:
                trend_type = 'stable'
            
            trends.append({
                'service': service,
                'trend': trend_type,
                'slope': round(slope, 2),
                'avg_change': round(avg_change, 2),
                'weeks_analyzed': len(service_df)
            })
    
    # Separate by trend type
    increasing = [t for t in trends if t['trend'] == 'increasing']
    decreasing = [t for t in trends if t['trend'] == 'decreasing']
    stable = [t for t in trends if t['trend'] == 'stable']
    
    # Sort by slope magnitude
    increasing.sort(key=lambda x: x['slope'], reverse=True)
    decreasing.sort(key=lambda x: x['slope'])
    
    return {
        'analysis_type': 'trend_detection',
        'increasing_trends': increasing[:20],
        'decreasing_trends': decreasing[:20],
        'stable_services': len(stable)
    }


def _multi_group_analysis(ce_client, accounts, weeks):
    """Multi-dimensional grouping (service + account)."""
    # Get drill-down data for all services
    drill_data = analyze_drill_down(ce_client, accounts, weeks)
    
    # Convert to DataFrame
    rows = []
    for comp in drill_data['comparisons']:
        week = comp['curr_week']['label']
        for item in comp['increases'] + comp['decreases']:
            rows.append({
                'week': week,
                'dimension': item['dimension'],  # This is account when drilling by service
                'change': item['change'],
                'curr_cost': item['curr_cost']
            })
    
    df = pd.DataFrame(rows)
    
    if df.empty:
        return {'error': 'No drill-down data available'}
    
    # Group by dimension (account) and aggregate
    grouped = df.groupby('dimension').agg({
        'change': ['sum', 'mean', 'count'],
        'curr_cost': 'sum'
    }).round(2)
    
    grouped.columns = ['total_change', 'avg_change', 'weeks_appeared', 'total_cost']
    grouped = grouped.sort_values('total_change', ascending=False).reset_index()
    
    return {
        'analysis_type': 'multi_group',
        'group_by': drill_data.get('group_by', 'account'),
        'groups': grouped.head(50).to_dict('records')
    }


def search_services(ce_client, accounts, weeks, pattern=None, min_cost=None):
    """
    Search and filter services.
    
    Args:
        ce_client: boto3 Cost Explorer client
        accounts: List of account IDs
        weeks: Number of weeks
        pattern: Service name pattern (e.g., "EC2*", "*Compute*")
        min_cost: Minimum total cost threshold
    
    Returns:
        dict with matching services
    """
    # Get trends data
    trends_data = analyze_trends(ce_client, accounts, weeks)
    
    # Convert to DataFrame
    rows = []
    for comp in trends_data['wow_comparisons']:
        for item in comp['increases'] + comp['decreases']:
            rows.append({
                'service': item['service'],
                'change': item['change'],
                'curr_cost': item['curr_cost']
            })
    
    df = pd.DataFrame(rows)
    
    if df.empty:
        return {'matches': []}
    
    # Aggregate by service
    summary = df.groupby('service').agg({
        'change': 'sum',
        'curr_cost': 'sum'
    }).reset_index()
    
    # Apply filters
    if pattern:
        # Convert glob pattern to regex
        import re
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        summary = summary[summary['service'].str.contains(regex_pattern, case=False, regex=True)]
    
    if min_cost:
        summary = summary[summary['curr_cost'] >= min_cost]
    
    # Sort by total cost
    summary = summary.sort_values('curr_cost', ascending=False)
    
    return {
        'pattern': pattern,
        'min_cost': min_cost,
        'matches': summary.to_dict('records')
    }
