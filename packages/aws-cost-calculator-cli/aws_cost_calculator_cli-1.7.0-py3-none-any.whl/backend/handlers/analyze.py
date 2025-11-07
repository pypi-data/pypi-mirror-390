"""
Lambda handler for pandas-based analysis.
"""
import json
import os
import boto3
from algorithms.analyze import analyze_aggregated, search_services


def handler(event, context):
    """Handle analysis requests."""
    
    # Parse request
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
    except:
        body = event
    
    # Validate API secret
    headers = event.get('headers', {})
    api_secret = headers.get('X-API-Secret') or headers.get('x-api-secret')
    
    secret_name = os.environ.get('SECRET_NAME', 'cost-calculator-api-secret')
    secrets_client = boto3.client('secretsmanager')
    
    try:
        secret_response = secrets_client.get_secret_value(SecretId=secret_name)
        expected_secret = secret_response['SecretString']
        
        if api_secret != expected_secret:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Unauthorized'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Secret validation failed: {str(e)}'})
        }
    
    # Get parameters
    credentials = body.get('credentials', {})
    accounts = body.get('accounts', [])
    weeks = body.get('weeks', 12)
    analysis_type = body.get('type', 'summary')
    
    # For search
    pattern = body.get('pattern')
    min_cost = body.get('min_cost')
    
    if not accounts:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'accounts required'})
        }
    
    try:
        # Create Cost Explorer client
        ce_client = boto3.client(
            'ce',
            region_name='us-east-1',
            aws_access_key_id=credentials['access_key'],
            aws_secret_access_key=credentials['secret_key'],
            aws_session_token=credentials.get('session_token')
        )
        
        # Run analysis
        if analysis_type == 'search':
            result = search_services(ce_client, accounts, weeks, pattern, min_cost)
        else:
            result = analyze_aggregated(ce_client, accounts, weeks, analysis_type)
        
        # Convert datetime objects and handle NaN/Infinity
        import math
        
        def convert_values(obj):
            if isinstance(obj, dict):
                return {k: convert_values(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_values(item) for item in obj]
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif isinstance(obj, float):
                if math.isnan(obj):
                    return None
                elif math.isinf(obj):
                    return None
            return obj
        
        result = convert_values(result)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
