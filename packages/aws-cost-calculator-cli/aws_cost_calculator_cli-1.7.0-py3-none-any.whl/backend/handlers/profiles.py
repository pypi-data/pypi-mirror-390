"""
Lambda handler for profile CRUD operations.
"""
import json
import os
import boto3
from datetime import datetime


def handler(event, context):
    """Handle profile CRUD operations."""
    
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
    
    # Get operation
    operation = body.get('operation')  # list, get, create, update, delete
    profile_name = body.get('profile_name')
    
    # DynamoDB table
    table_name = os.environ.get('PROFILES_TABLE', 'cost-calculator-profiles')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        if operation == 'list':
            # List all profiles
            response = table.scan()
            profiles = response.get('Items', [])
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'profiles': profiles})
            }
        
        elif operation == 'get':
            # Get specific profile
            if not profile_name:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'profile_name required'})
                }
            
            response = table.get_item(Key={'profile_name': profile_name})
            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Profile not found'})
                }
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'profile': response['Item']})
            }
        
        elif operation == 'create' or operation == 'update':
            # Create or update profile
            if not profile_name:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'profile_name required'})
                }
            
            accounts = body.get('accounts', [])
            description = body.get('description', '')
            
            item = {
                'profile_name': profile_name,
                'accounts': accounts,
                'description': description,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if operation == 'create':
                item['created_at'] = datetime.utcnow().isoformat()
            
            table.put_item(Item=item)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Profile saved', 'profile': item})
            }
        
        elif operation == 'delete':
            # Delete profile
            if not profile_name:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'profile_name required'})
                }
            
            table.delete_item(Key={'profile_name': profile_name})
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Profile deleted'})
            }
        
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid operation. Use: list, get, create, update, delete'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
