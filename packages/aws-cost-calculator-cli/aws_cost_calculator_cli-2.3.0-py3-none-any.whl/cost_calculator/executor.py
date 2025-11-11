"""
Executor that routes to either API or local execution.
"""
import boto3
import click
from pathlib import Path
from cost_calculator.api_client import is_api_configured, call_lambda_api


def get_credentials_dict(config):
    """
    Extract credentials from config in format needed for API.
    
    Returns:
        dict with access_key, secret_key, session_token, or None if profile is 'dummy'
    """
    if 'aws_profile' in config:
        # Skip credential loading for dummy profile (API-only mode)
        if config['aws_profile'] == 'dummy':
            return None
        
        # Get temporary credentials from SSO session
        try:
            session = boto3.Session(profile_name=config['aws_profile'])
            credentials = session.get_credentials()
            
            if credentials is None:
                raise Exception(
                    f"Could not get credentials for profile '{config['aws_profile']}'.\n"
                    f"Run: aws sso login --profile {config['aws_profile']}"
                )
            
            frozen_creds = credentials.get_frozen_credentials()
            
            return {
                'access_key': frozen_creds.access_key,
                'secret_key': frozen_creds.secret_key,
                'session_token': frozen_creds.token
            }
        except Exception as e:
            # Show the actual error instead of silently returning None
            error_msg = str(e)
            
            # If it's an SSO token error, provide better guidance
            if 'SSO Token' in error_msg or 'sso' in error_msg.lower():
                # Try to detect if using sso_session format
                import subprocess
                try:
                    result = subprocess.run(
                        ['grep', '-A', '3', f'profile {config["aws_profile"]}', 
                         str(Path.home() / '.aws' / 'config')],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if 'sso_session' in result.stdout:
                        # Extract session name
                        for line in result.stdout.split('\n'):
                            if 'sso_session' in line:
                                session_name = line.split('=')[1].strip()
                                raise Exception(
                                    f"Failed to get AWS credentials for profile '{config['aws_profile']}'.\n"
                                    f"Error: {error_msg}\n\n"
                                    f"Your profile uses SSO session '{session_name}'.\n"
                                    f"Try: aws sso login --sso-session {session_name}\n"
                                    f"(Requires AWS CLI v2.9.0+)\n\n"
                                    f"Or: aws sso login --profile {config['aws_profile']}\n"
                                    f"(If using older AWS CLI)"
                                )
                except:
                    pass
            
            raise Exception(
                f"Failed to get AWS credentials for profile '{config['aws_profile']}'.\n"
                f"Error: {error_msg}\n"
                f"Try: aws sso login --profile {config['aws_profile']}"
            )
    else:
        # Use static credentials
        creds = config.get('credentials', {})
        if not creds:
            return None
        
        result = {
            'access_key': creds['aws_access_key_id'],
            'secret_key': creds['aws_secret_access_key']
        }
        if 'aws_session_token' in creds:
            result['session_token'] = creds['aws_session_token']
        return result


def execute_trends(config, weeks):
    """
    Execute trends analysis via API.
    
    Args:
        config: Profile configuration
        weeks: Number of weeks to analyze
    
    Returns:
        dict: trends data
    """
    profile_name = config.get('profile_name', config.get('name'))
    
    if not is_api_configured():
        raise Exception(
            "API not configured. Set COST_API_SECRET environment variable.\n"
            "Local execution is disabled. Use the Lambda API."
        )
    
    # Use API only
    click.echo("Using Lambda API...")
    credentials = get_credentials_dict(config)
    if not credentials:
        raise Exception("Failed to get AWS credentials. Check your AWS SSO session.")
    return call_lambda_api('trends', credentials, profile=profile_name, weeks=weeks)


def execute_monthly(config, months):
    """
    Execute monthly analysis via API or locally.
    
    Returns:
        dict: monthly data
    """
    profile_name = config.get('profile_name', config.get('name'))
    
    if not is_api_configured():
        raise Exception(
            "API not configured. Set COST_API_SECRET environment variable.\n"
            "Local execution is disabled. Use the Lambda API."
        )
    
    # Use API only
    click.echo("Using Lambda API...")
    credentials = get_credentials_dict(config)
    if not credentials:
        raise Exception("Failed to get AWS credentials. Check your AWS SSO session.")
    return call_lambda_api('monthly', credentials, profile=profile_name, months=months)


def execute_drill(config, weeks, service_filter=None, account_filter=None, usage_type_filter=None, resources=False, dimension=None, backend='auto'):
    """
    Execute drill-down analysis via API.
    
    Args:
        config: Profile configuration
        weeks: Number of weeks to analyze
        service_filter: Optional service name filter
        account_filter: Optional account ID filter
        usage_type_filter: Optional usage type filter
        resources: If True, query CUR for resource-level details
        dimension: Dimension to analyze by (service, account, region, usage_type, resource, etc.)
        backend: Backend to use ('auto', 'ce', 'athena')
    
    Returns:
        dict: drill data or resource data
    """
    profile_name = config.get('profile_name', config.get('name'))
    
    if not is_api_configured():
        raise Exception(
            "API not configured. Set COST_API_SECRET environment variable.\n"
            "Local execution is disabled. Use the Lambda API."
        )
    
    # Use API only
    click.echo("Using Lambda API...")
    credentials = get_credentials_dict(config)
    if not credentials:
        raise Exception("Failed to get AWS credentials. Check your AWS SSO session.")
    
    kwargs = {'weeks': weeks}
    if service_filter:
        kwargs['service'] = service_filter
    if account_filter:
        kwargs['account'] = account_filter
    if usage_type_filter:
        kwargs['usage_type'] = usage_type_filter
    if dimension:
        kwargs['dimension'] = dimension
    if backend and backend != 'auto':
        kwargs['backend'] = backend
    if resources:
        if not service_filter and not dimension:
            raise click.ClickException("--service or --dimension is required when using --resources flag")
        kwargs['resources'] = True
    
    return call_lambda_api('drill', credentials, profile=profile_name, **kwargs)


def execute_analyze(config, weeks, analysis_type, pattern=None, min_cost=None):
    """
    Execute pandas-based analysis via API.
    Note: This only works via API (requires pandas layer).
    
    Returns:
        dict: analysis results
    """
    accounts = config['accounts']
    
    if not is_api_configured():
        raise click.ClickException(
            "Analyze command requires API configuration.\n"
            "Set COST_API_SECRET environment variable."
        )
    
    credentials = get_credentials_dict(config)
    kwargs = {'weeks': weeks, 'type': analysis_type}
    
    if pattern:
        kwargs['pattern'] = pattern
    if min_cost:
        kwargs['min_cost'] = min_cost
    
    return call_lambda_api('analyze', credentials, accounts, **kwargs)


def execute_profile_operation(operation, profile_name=None, accounts=None, description=None):
    """
    Execute profile CRUD operations via API.
    
    Returns:
        dict: operation result
    """
    if not is_api_configured():
        raise click.ClickException(
            "Profile commands require API configuration.\n"
            "Set COST_API_SECRET environment variable."
        )
    
    # Profile operations don't need AWS credentials, just API secret
    import os
    import requests
    import json
    
    api_secret = os.environ.get('COST_API_SECRET', '')
    
    # Use profiles endpoint (can be overridden via environment variable)
    url = os.environ.get(
        'COST_CALCULATOR_PROFILES_URL',
        'https://64g7jq7sjygec2zmll5lsghrpi0txrzo.lambda-url.us-east-1.on.aws/'
    )
    
    payload = {'operation': operation}
    if profile_name:
        payload['profile_name'] = profile_name
    if accounts:
        payload['accounts'] = accounts
    if description:
        payload['description'] = description
    
    headers = {
        'X-API-Secret': api_secret,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    return response.json()
