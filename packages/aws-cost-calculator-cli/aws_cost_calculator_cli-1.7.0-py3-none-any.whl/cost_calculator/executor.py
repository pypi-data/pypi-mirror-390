"""
Executor that routes to either API or local execution.
"""
import boto3
import click
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
            frozen_creds = credentials.get_frozen_credentials()
            
            return {
                'access_key': frozen_creds.access_key,
                'secret_key': frozen_creds.secret_key,
                'session_token': frozen_creds.token
            }
        except Exception:
            # If profile not found, return None (API will handle)
            return None
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
    Execute trends analysis via API or locally.
    
    Returns:
        dict: trends data
    """
    accounts = config['accounts']
    
    if is_api_configured():
        # Use API
        click.echo("Using Lambda API...")
        credentials = get_credentials_dict(config)
        return call_lambda_api('trends', credentials, accounts, weeks=weeks)
    else:
        # Use local execution
        click.echo("Using local execution...")
        from cost_calculator.trends import analyze_trends
        
        # Initialize boto3 client
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session_kwargs = {
                'aws_access_key_id': creds['aws_access_key_id'],
                'aws_secret_access_key': creds['aws_secret_access_key'],
                'region_name': creds.get('region', 'us-east-1')
            }
            if 'aws_session_token' in creds:
                session_kwargs['aws_session_token'] = creds['aws_session_token']
            session = boto3.Session(**session_kwargs)
        
        ce_client = session.client('ce', region_name='us-east-1')
        return analyze_trends(ce_client, accounts, weeks)


def execute_monthly(config, months):
    """
    Execute monthly analysis via API or locally.
    
    Returns:
        dict: monthly data
    """
    accounts = config['accounts']
    
    if is_api_configured():
        # Use API
        click.echo("Using Lambda API...")
        credentials = get_credentials_dict(config)
        return call_lambda_api('monthly', credentials, accounts, months=months)
    else:
        # Use local execution
        click.echo("Using local execution...")
        from cost_calculator.monthly import analyze_monthly_trends
        
        # Initialize boto3 client
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session_kwargs = {
                'aws_access_key_id': creds['aws_access_key_id'],
                'aws_secret_access_key': creds['aws_secret_access_key'],
                'region_name': creds.get('region', 'us-east-1')
            }
            if 'aws_session_token' in creds:
                session_kwargs['aws_session_token'] = creds['aws_session_token']
            session = boto3.Session(**session_kwargs)
        
        ce_client = session.client('ce', region_name='us-east-1')
        return analyze_monthly_trends(ce_client, accounts, months)


def execute_drill(config, weeks, service_filter=None, account_filter=None, usage_type_filter=None, resources=False):
    """
    Execute drill-down analysis via API or locally.
    
    Args:
        config: Profile configuration
        weeks: Number of weeks to analyze
        service_filter: Optional service name filter
        account_filter: Optional account ID filter
        usage_type_filter: Optional usage type filter
        resources: If True, query CUR for resource-level details
    
    Returns:
        dict: drill data or resource data
    """
    accounts = config['accounts']
    
    if resources:
        # Resource-level drill requires service filter
        if not service_filter:
            raise click.ClickException("--service is required when using --resources flag")
        
        if is_api_configured():
            # Use API
            click.echo("Using Lambda API for CUR resource query...")
            credentials = get_credentials_dict(config)
            kwargs = {
                'weeks': weeks,
                'service': service_filter,
                'resources': True
            }
            if account_filter:
                kwargs['account'] = account_filter
            return call_lambda_api('drill', credentials, accounts, **kwargs)
        else:
            # Use local Athena client
            click.echo("Using local Athena client for CUR resource query...")
            from cost_calculator.cur import query_cur_resources
            
            # Initialize boto3 session
            if 'aws_profile' in config:
                session = boto3.Session(profile_name=config['aws_profile'])
            else:
                creds = config['credentials']
                session_kwargs = {
                    'aws_access_key_id': creds['aws_access_key_id'],
                    'aws_secret_access_key': creds['aws_secret_access_key'],
                    'region_name': creds.get('region', 'us-east-1')
                }
                if 'aws_session_token' in creds:
                    session_kwargs['aws_session_token'] = creds['aws_session_token']
                session = boto3.Session(**session_kwargs)
            
            athena_client = session.client('athena', region_name='us-east-1')
            return query_cur_resources(
                athena_client, accounts, service_filter, account_filter, weeks
            )
    else:
        # Standard drill-down via Cost Explorer
        if is_api_configured():
            # Use API
            click.echo("Using Lambda API...")
            credentials = get_credentials_dict(config)
            kwargs = {'weeks': weeks}
            if service_filter:
                kwargs['service'] = service_filter
            if account_filter:
                kwargs['account'] = account_filter
            if usage_type_filter:
                kwargs['usage_type'] = usage_type_filter
            return call_lambda_api('drill', credentials, accounts, **kwargs)
        else:
            # Use local execution
            click.echo("Using local execution...")
            from cost_calculator.drill import analyze_drill_down
            
            # Initialize boto3 client
            if 'aws_profile' in config:
                session = boto3.Session(profile_name=config['aws_profile'])
            else:
                creds = config['credentials']
                session_kwargs = {
                    'aws_access_key_id': creds['aws_access_key_id'],
                    'aws_secret_access_key': creds['aws_secret_access_key'],
                    'region_name': creds.get('region', 'us-east-1')
                }
                if 'aws_session_token' in creds:
                    session_kwargs['aws_session_token'] = creds['aws_session_token']
                session = boto3.Session(**session_kwargs)
            
            ce_client = session.client('ce', region_name='us-east-1')
            return analyze_drill_down(
                ce_client, accounts, weeks,
                service_filter=service_filter,
                account_filter=account_filter,
                usage_type_filter=usage_type_filter
            )


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
    
    # Use profiles endpoint (hardcoded URL)
    url = 'https://64g7jq7sjygec2zmll5lsghrpi0txrzo.lambda-url.us-east-1.on.aws/'
    
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
