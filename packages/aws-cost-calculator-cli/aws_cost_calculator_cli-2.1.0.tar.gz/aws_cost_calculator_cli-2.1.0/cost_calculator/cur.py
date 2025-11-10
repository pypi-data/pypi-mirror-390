"""
CUR (Cost and Usage Report) queries via Athena for resource-level analysis.
"""
import time
from datetime import datetime, timedelta


# Service name to CUR product code mapping
SERVICE_TO_PRODUCT_CODE = {
    'EC2 - Other': 'AmazonEC2',
    'Amazon Elastic Compute Cloud - Compute': 'AmazonEC2',
    'Amazon Relational Database Service': 'AmazonRDS',
    'Amazon Simple Storage Service': 'AmazonS3',
    'Load Balancing': 'AWSELB',
    'Elastic Load Balancing': 'AWSELB',
    'Amazon DynamoDB': 'AmazonDynamoDB',
    'AWS Lambda': 'AWSLambda',
    'Amazon CloudFront': 'AmazonCloudFront',
    'Amazon ElastiCache': 'AmazonElastiCache',
    'Amazon Elastic MapReduce': 'ElasticMapReduce',
    'Amazon Kinesis': 'AmazonKinesis',
    'Amazon Redshift': 'AmazonRedshift',
    'Amazon Simple Notification Service': 'AmazonSNS',
    'Amazon Simple Queue Service': 'AmazonSQS',
}


def map_service_to_product_code(service_name):
    """Map service name to CUR product code"""
    # Direct mapping
    if service_name in SERVICE_TO_PRODUCT_CODE:
        return SERVICE_TO_PRODUCT_CODE[service_name]
    
    # Fuzzy matching
    service_lower = service_name.lower()
    for key, code in SERVICE_TO_PRODUCT_CODE.items():
        if key.lower() in service_lower or service_lower in key.lower():
            return code
    
    # Fallback: try to extract from service name
    # "Amazon Relational Database Service" -> "AmazonRDS"
    return service_name.replace(' ', '').replace('-', '')


def get_cur_config():
    """Load CUR configuration from config file or environment variables"""
    import os
    from pathlib import Path
    import json
    
    # Try config file first
    config_file = Path.home() / '.config' / 'cost-calculator' / 'cur_config.json'
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    
    # Fall back to environment variables
    return {
        'database': os.environ.get('CUR_DATABASE', 'cur_database'),
        'table': os.environ.get('CUR_TABLE', 'cur_table'),
        's3_output': os.environ.get('CUR_S3_OUTPUT', 's3://your-athena-results-bucket/')
    }


def query_cur_resources(athena_client, accounts, service, account_filter, weeks, 
                       cur_database=None,
                       cur_table=None,
                       s3_output=None):
    """
    Query CUR via Athena for resource-level cost details.
    
    Args:
        athena_client: boto3 Athena client
        accounts: list of account IDs
        service: service name to filter by
        account_filter: specific account ID or None for all accounts
        weeks: number of weeks to analyze
        cur_database: Athena database name
        cur_table: CUR table name
        s3_output: S3 location for query results
    
    Returns:
        list of dicts with resource details
    """
    # Load CUR configuration
    cur_config = get_cur_config()
    if cur_database is None:
        cur_database = cur_config['database']
    if cur_table is None:
        cur_table = cur_config['table']
    if s3_output is None:
        s3_output = cur_config['s3_output']
    
    # Calculate date range
    end_date = datetime.now() - timedelta(days=2)
    start_date = end_date - timedelta(weeks=weeks)
    
    # Map service to product code
    product_code = map_service_to_product_code(service)
    
    # Build account filter
    if account_filter:
        account_clause = f"AND line_item_usage_account_id = '{account_filter}'"
    else:
        account_list = "','".join(accounts)
        account_clause = f"AND line_item_usage_account_id IN ('{account_list}')"
    
    # Build query - use generic columns that work for all services
    query = f"""
    SELECT 
        line_item_usage_account_id as account_id,
        line_item_resource_id as resource_id,
        line_item_usage_type as usage_type,
        product_region as region,
        SUM(line_item_unblended_cost) as total_cost,
        SUM(line_item_usage_amount) as total_usage
    FROM {cur_database}.{cur_table}
    WHERE line_item_product_code = '{product_code}'
      {account_clause}
      AND line_item_resource_id != ''
      AND line_item_line_item_type IN ('Usage', 'Fee')
      AND line_item_usage_start_date >= DATE '{start_date.strftime('%Y-%m-%d')}'
      AND line_item_usage_start_date < DATE '{end_date.strftime('%Y-%m-%d')}'
    GROUP BY 1, 2, 3, 4
    ORDER BY total_cost DESC
    LIMIT 50
    """
    
    # Execute Athena query
    try:
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': cur_database},
            ResultConfiguration={'OutputLocation': s3_output}
        )
        
        query_execution_id = response['QueryExecutionId']
        
        # Wait for query to complete (max 60 seconds)
        max_wait = 60
        wait_interval = 2
        elapsed = 0
        
        while elapsed < max_wait:
            status_response = athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            state = status_response['QueryExecution']['Status']['State']
            
            if state == 'SUCCEEDED':
                break
            elif state in ['FAILED', 'CANCELLED']:
                reason = status_response['QueryExecution']['Status'].get(
                    'StateChangeReason', 'Unknown error'
                )
                raise Exception(f"Athena query {state}: {reason}")
            
            time.sleep(wait_interval)
            elapsed += wait_interval
        
        if elapsed >= max_wait:
            raise Exception("Athena query timeout after 60 seconds")
        
        # Get results
        results_response = athena_client.get_query_results(
            QueryExecutionId=query_execution_id,
            MaxResults=100
        )
        
        # Parse results
        resources = []
        rows = results_response['ResultSet']['Rows']
        
        # Skip header row
        for row in rows[1:]:
            data = row['Data']
            resources.append({
                'account_id': data[0].get('VarCharValue', ''),
                'resource_id': data[1].get('VarCharValue', ''),
                'usage_type': data[2].get('VarCharValue', ''),
                'region': data[3].get('VarCharValue', ''),
                'total_cost': float(data[4].get('VarCharValue', 0)),
                'total_usage': float(data[5].get('VarCharValue', 0))
            })
        
        return {
            'resources': resources,
            'service': service,
            'product_code': product_code,
            'account_filter': account_filter,
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'weeks': weeks
            }
        }
        
    except Exception as e:
        raise Exception(f"CUR query failed: {str(e)}")


def format_resource_output(result):
    """Format resource query results for display"""
    resources = result['resources']
    service = result['service']
    account_filter = result.get('account_filter')
    period = result['period']
    
    output = []
    output.append(f"\n📊 Resource Breakdown: {service}")
    
    if account_filter:
        output.append(f"Account: {account_filter} | Period: {period['start']} to {period['end']} ({period['weeks']} weeks)")
    else:
        output.append(f"All Accounts | Period: {period['start']} to {period['end']} ({period['weeks']} weeks)")
    
    output.append("")
    
    if not resources:
        output.append("No resources found with costs in this period.")
        return '\n'.join(output)
    
    # Format as table
    output.append(f"Top {len(resources)} Resources by Cost:")
    output.append("┌─────────────────────────────┬──────────────────────────────┬────────────┬─────────┐")
    output.append("│ Resource ID                 │ Usage Type                   │ Region     │ Cost    │")
    output.append("├─────────────────────────────┼──────────────────────────────┼────────────┼─────────┤")
    
    for resource in resources:
        resource_id = resource['resource_id'][:27] + '...' if len(resource['resource_id']) > 27 else resource['resource_id']
        usage_type = resource['usage_type'][:28] + '..' if len(resource['usage_type']) > 28 else resource['usage_type']
        region = resource['region'][:10] if resource['region'] else 'N/A'
        cost = resource['total_cost']
        
        output.append(
            f"│ {resource_id:<27} │ {usage_type:<28} │ {region:<10} │ ${cost:>6.2f} │"
        )
    
    output.append("└─────────────────────────────┴──────────────────────────────┴────────────┴─────────┘")
    output.append("")
    output.append("💡 Tip: Use AWS CLI to investigate specific resources:")
    output.append(f"  aws ec2 describe-instances --instance-ids <resource-id>")
    
    return '\n'.join(output)
