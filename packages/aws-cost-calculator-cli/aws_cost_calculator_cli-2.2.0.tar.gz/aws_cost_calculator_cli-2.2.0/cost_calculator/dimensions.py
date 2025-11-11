"""
Dimension mapping between CLI, Cost Explorer, and Athena CUR.

This module provides utilities for translating dimension names across different backends.
"""

# Dimension mapping: CLI dimension -> (CE dimension, Athena column)
DIMENSION_MAP = {
    'service': ('SERVICE', 'line_item_product_code'),
    'account': ('LINKED_ACCOUNT', 'line_item_usage_account_id'),
    'region': ('REGION', 'product_region'),
    'usage_type': ('USAGE_TYPE', 'line_item_usage_type'),
    'resource': (None, 'line_item_resource_id'),  # Athena only
    'instance_type': ('INSTANCE_TYPE', 'product_instance_type'),
    'operation': ('OPERATION', 'line_item_operation'),
    'availability_zone': ('AVAILABILITY_ZONE', 'product_availability_zone'),
}


def get_ce_dimension(cli_dimension):
    """
    Get Cost Explorer dimension key for a CLI dimension.
    
    Args:
        cli_dimension: CLI dimension name (e.g., 'service', 'account')
    
    Returns:
        str: Cost Explorer dimension key (e.g., 'SERVICE', 'LINKED_ACCOUNT')
        None: If dimension is not available in Cost Explorer
    
    Raises:
        ValueError: If dimension is unknown
    """
    if cli_dimension not in DIMENSION_MAP:
        raise ValueError(f"Unknown dimension: {cli_dimension}")
    
    ce_dim, _ = DIMENSION_MAP[cli_dimension]
    return ce_dim


def get_athena_column(cli_dimension):
    """
    Get Athena CUR column name for a CLI dimension.
    
    Args:
        cli_dimension: CLI dimension name (e.g., 'service', 'account')
    
    Returns:
        str: Athena column name (e.g., 'line_item_product_code', 'line_item_usage_account_id')
    
    Raises:
        ValueError: If dimension is unknown
    """
    if cli_dimension not in DIMENSION_MAP:
        raise ValueError(f"Unknown dimension: {cli_dimension}")
    
    _, athena_col = DIMENSION_MAP[cli_dimension]
    return athena_col


def is_athena_only(cli_dimension):
    """
    Check if a dimension is only available in Athena (not in Cost Explorer).
    
    Args:
        cli_dimension: CLI dimension name
    
    Returns:
        bool: True if dimension requires Athena, False otherwise
    """
    if cli_dimension not in DIMENSION_MAP:
        raise ValueError(f"Unknown dimension: {cli_dimension}")
    
    ce_dim, _ = DIMENSION_MAP[cli_dimension]
    return ce_dim is None


def get_available_dimensions(backend='auto'):
    """
    Get list of available dimensions for a given backend.
    
    Args:
        backend: 'auto', 'ce', or 'athena'
    
    Returns:
        list: List of available dimension names
    """
    if backend == 'athena':
        # All dimensions available in Athena
        return list(DIMENSION_MAP.keys())
    elif backend == 'ce':
        # Only dimensions with CE mapping
        return [dim for dim, (ce_dim, _) in DIMENSION_MAP.items() if ce_dim is not None]
    else:  # auto
        # All dimensions (backend will be auto-selected)
        return list(DIMENSION_MAP.keys())


def validate_dimension_backend(dimension, backend):
    """
    Validate that a dimension is available for the specified backend.
    
    Args:
        dimension: CLI dimension name
        backend: 'auto', 'ce', or 'athena'
    
    Returns:
        tuple: (is_valid, error_message)
    
    Examples:
        >>> validate_dimension_backend('resource', 'ce')
        (False, "Dimension 'resource' requires Athena backend (not available in Cost Explorer)")
        
        >>> validate_dimension_backend('service', 'ce')
        (True, None)
    """
    if dimension not in DIMENSION_MAP:
        return False, f"Unknown dimension: {dimension}"
    
    if backend == 'ce' and is_athena_only(dimension):
        return False, f"Dimension '{dimension}' requires Athena backend (not available in Cost Explorer)"
    
    return True, None


# Human-readable dimension descriptions
DIMENSION_DESCRIPTIONS = {
    'service': 'AWS Service (e.g., EC2, S3, RDS)',
    'account': 'AWS Account ID',
    'region': 'AWS Region (e.g., us-east-1, eu-west-1)',
    'usage_type': 'Usage Type (e.g., BoxUsage:t3.micro)',
    'resource': 'Resource ID/ARN (Athena only)',
    'instance_type': 'Instance Type (e.g., t3.micro, m5.large)',
    'operation': 'Operation (e.g., RunInstances, CreateBucket)',
    'availability_zone': 'Availability Zone (e.g., us-east-1a)',
}


def get_dimension_description(dimension):
    """Get human-readable description for a dimension."""
    return DIMENSION_DESCRIPTIONS.get(dimension, dimension)
