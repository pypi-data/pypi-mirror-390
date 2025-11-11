"""
API client for calling Lambda backend.
Falls back to local execution if API is not configured.
"""
import os
import json
import requests
from pathlib import Path


def get_api_config():
    """
    Get API configuration.
    
    Returns:
        dict: API configuration with api_secret, or None if not configured
    """
    api_secret = os.environ.get('COST_API_SECRET', '')
    
    if api_secret:
        return {'api_secret': api_secret}
    
    return None


def call_lambda_api(endpoint, credentials, accounts=None, profile=None, **kwargs):
    """
    Call unified API Gateway endpoint.
    
    Args:
        endpoint: API endpoint name ('calculate', 'trends', 'monthly', 'drill', 'query', etc.)
        credentials: dict with AWS credentials
        accounts: list of account IDs (deprecated - use profile instead)
        profile: profile name (preferred over accounts)
        **kwargs: additional parameters for the specific endpoint
    
    Returns:
        dict: API response data
    
    Raises:
        Exception: if API call fails
    """
    api_config = get_api_config()
    
    if not api_config:
        raise Exception("API not configured. Set COST_API_SECRET environment variable.")
    
    # Get base URL from environment or use default
    base_url = os.environ.get('COST_CALCULATOR_API_URL', 'https://api.costcop.cloudfix.dev')
    url = f"{base_url}/{endpoint}"
    
    # Build request payload
    payload = {
        'credentials': credentials
    }
    
    # Add profile or accounts
    if profile:
        payload['profile'] = profile
    elif accounts:
        payload['accounts'] = accounts
    
    # Add additional parameters
    payload.update(kwargs)
    
    # Make API call
    headers = {
        'X-API-Secret': api_config['api_secret'],
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=900)  # 15 min timeout
    
    if response.status_code != 200:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    return response.json()


def is_api_configured():
    """Check if API is configured."""
    return get_api_config() is not None
