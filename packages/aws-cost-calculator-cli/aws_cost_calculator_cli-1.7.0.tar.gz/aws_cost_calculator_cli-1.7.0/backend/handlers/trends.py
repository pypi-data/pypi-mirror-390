"""
Lambda handler for trends analysis.
"""
import json
import boto3
import os
from algorithms.trends import analyze_trends

# Get API secret from Secrets Manager
secrets_client = boto3.client('secretsmanager')
api_secret_arn = os.environ['API_SECRET_ARN']
api_secret = secrets_client.get_secret_value(SecretId=api_secret_arn)['SecretString']


def handler(event, context):
    """
    Lambda handler for trends analysis.
    
    Expected event:
    {
        "credentials": {
            "access_key": "AKIA...",
            "secret_key": "...",
            "session_token": "..." (optional)
        },
        "accounts": ["123456789012", "987654321098"],
        "weeks": 4
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
        weeks = body.get('weeks', 3)
        
        if not credentials or not accounts:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Missing credentials or accounts'})
            }
        
        # Create Cost Explorer client with provided credentials
        ce_client = boto3.client(
            'ce',
            region_name='us-east-1',
            aws_access_key_id=credentials['access_key'],
            aws_secret_access_key=credentials['secret_key'],
            aws_session_token=credentials.get('session_token')
        )
        
        # Run analysis
        trends_data = analyze_trends(ce_client, accounts, weeks)
        
        # Convert datetime objects to strings for JSON serialization
        def convert_dates(obj):
            if isinstance(obj, dict):
                return {k: convert_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_dates(item) for item in obj]
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return obj
        
        trends_data = convert_dates(trends_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(trends_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
