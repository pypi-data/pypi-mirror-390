"""
Lambda handler for drill-down analysis.
"""
import json
import boto3
import os
from algorithms.drill import analyze_drill_down
from algorithms.cur import query_cur_resources

# Get API secret from Secrets Manager
secrets_client = boto3.client('secretsmanager')
api_secret_arn = os.environ['API_SECRET_ARN']
api_secret = secrets_client.get_secret_value(SecretId=api_secret_arn)['SecretString']


def handler(event, context):
    """
    Lambda handler for drill-down analysis.
    
    Expected event:
    {
        "credentials": {
            "access_key": "AKIA...",
            "secret_key": "...",
            "session_token": "..." (optional)
        },
        "accounts": ["123456789012"],
        "weeks": 4,
        "service": "EC2 - Other" (optional),
        "account": "123456789012" (optional),
        "usage_type": "DataTransfer-Out-Bytes" (optional)
    }
    """
    # Handle OPTIONS for CORS
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Validate API secret
        headers = event.get('headers', {})
        provided_secret = headers.get('x-api-secret') or headers.get('X-API-Secret')
        
        if provided_secret != api_secret:
            return {
                'statusCode': 401,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        credentials = body.get('credentials', {})
        accounts = body.get('accounts', [])
        weeks = body.get('weeks', 4)
        service_filter = body.get('service')
        account_filter = body.get('account')
        usage_type_filter = body.get('usage_type')
        resources = body.get('resources', False)
        
        if not credentials or not accounts:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Missing credentials or accounts'})
            }
        
        # Create clients with provided credentials
        ce_client = boto3.client(
            'ce',
            region_name='us-east-1',
            aws_access_key_id=credentials['access_key'],
            aws_secret_access_key=credentials['secret_key'],
            aws_session_token=credentials.get('session_token')
        )
        
        # Check if resource-level drill is requested
        if resources:
            if not service_filter:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'service parameter required for resource-level drill'})
                }
            
            # Create Athena client for CUR queries
            athena_client = boto3.client(
                'athena',
                region_name='us-east-1',
                aws_access_key_id=credentials['access_key'],
                aws_secret_access_key=credentials['secret_key'],
                aws_session_token=credentials.get('session_token')
            )
            
            # Run CUR resource query
            drill_data = query_cur_resources(
                athena_client, accounts, service_filter, account_filter, weeks
            )
        else:
            # Run standard drill analysis
            drill_data = analyze_drill_down(
                ce_client, accounts, weeks,
                service_filter=service_filter,
                account_filter=account_filter,
                usage_type_filter=usage_type_filter
            )
        
        # Convert datetime objects to strings for JSON serialization
        def convert_dates(obj):
            if isinstance(obj, dict):
                return {k: convert_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_dates(item) for item in obj]
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return obj
        
        drill_data = convert_dates(drill_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(drill_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
