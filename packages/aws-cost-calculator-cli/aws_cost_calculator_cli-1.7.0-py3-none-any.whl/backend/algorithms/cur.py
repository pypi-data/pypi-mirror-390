"""
CUR (Cost and Usage Report) queries via Athena for resource-level analysis.
Backend version for Lambda execution.
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
    
    # Fallback
    return service_name.replace(' ', '').replace('-', '')


def get_cur_config():
    """Load CUR configuration from environment variables"""
    import os
    
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
        dict with resource details
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
    
    # Build query
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
        
        # Wait for query to complete
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
            raise Exception("Athena query timeout")
        
        # Get results
        results_response = athena_client.get_query_results(
            QueryExecutionId=query_execution_id,
            MaxResults=100
        )
        
        # Parse results
        resources = []
        rows = results_response['ResultSet']['Rows']
        
        for row in rows[1:]:  # Skip header
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
