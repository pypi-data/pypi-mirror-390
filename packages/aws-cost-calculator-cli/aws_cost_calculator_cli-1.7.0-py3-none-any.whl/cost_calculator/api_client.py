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


def call_lambda_api(endpoint, credentials, accounts, **kwargs):
    """
    Call Lambda API endpoint.
    
    Args:
        endpoint: API endpoint name ('trends', 'monthly', 'drill')
        credentials: dict with AWS credentials
        accounts: list of account IDs
        **kwargs: additional parameters for the specific endpoint
    
    Returns:
        dict: API response data
    
    Raises:
        Exception: if API call fails
    """
    api_config = get_api_config()
    
    if not api_config:
        raise Exception("API not configured. Set COST_API_SECRET environment variable.")
    
    # Map endpoint names to Lambda URLs
    endpoint_urls = {
        'trends': 'https://pq3mqntc6vuwi4zw5flulsoleq0yiqtl.lambda-url.us-east-1.on.aws/',
        'monthly': 'https://6aueebodw6q4zdeu3aaexb6tle0fqhhr.lambda-url.us-east-1.on.aws/',
        'drill': 'https://3ncm2gzxrsyptrhud3ua3x5lju0akvsr.lambda-url.us-east-1.on.aws/',
        'analyze': 'https://y6npmidtxwzg62nrqzkbacfs5q0edwgs.lambda-url.us-east-1.on.aws/',
        'profiles': 'https://64g7jq7sjygec2zmll5lsghrpi0txrzo.lambda-url.us-east-1.on.aws/'
    }
    
    url = endpoint_urls.get(endpoint)
    
    if not url:
        raise Exception(f"Unknown endpoint: {endpoint}")
    
    # Build request payload
    payload = {
        'credentials': credentials,
        'accounts': accounts
    }
    payload.update(kwargs)
    
    # Make API call
    headers = {
        'X-API-Secret': api_config['api_secret'],
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=300)
    
    if response.status_code != 200:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    return response.json()


def is_api_configured():
    """Check if API is configured."""
    return get_api_config() is not None
