"""
Validation utilities for Unified STAC Client
"""

import requests
from urllib.parse import urlparse


def validate_stac_endpoint(endpoint_url, session=None):
    """
    Validate that an endpoint is a valid STAC API.
    
    Parameters
    ----------
    endpoint_url : str
        STAC API endpoint URL
    session : requests.Session, optional
        Session to use for requests
        
    Returns
    -------
    bool
        True if valid STAC endpoint
        
    Raises
    ------
    ValueError
        If endpoint is not valid
    """
    if not session:
        session = requests.Session()
    
    try:
        # Parse URL
        parsed_url = urlparse(endpoint_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format: {}".format(endpoint_url))
        
        # Try to access endpoint
        response = session.get(endpoint_url, timeout=10)
        response.raise_for_status()
        
        # Basic validation - should return JSON
        try:
            response.json()
        except ValueError:
            raise ValueError("Endpoint does not return valid JSON")
        
        return True
        
    except requests.RequestException as e:
        raise ValueError("Failed to connect to endpoint: {}".format(e))


def validate_search_params(params):
    """
    Validate search parameters.
    
    Parameters
    ----------
    params : dict
        Search parameters
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If parameters are invalid
    """
    # Validate bbox
    if 'bbox' in params and params['bbox']:
        bbox = params['bbox']
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise ValueError("bbox must be a list of 4 numbers [west, south, east, north]")
        
        west, south, east, north = bbox
        if not all(isinstance(coord, (int, float)) for coord in bbox):
            raise ValueError("bbox coordinates must be numbers")
        
        if west >= east or south >= north:
            raise ValueError("Invalid bbox: west >= east or south >= north")
    
    # Validate collections
    if 'collections' in params and params['collections']:
        if not isinstance(params['collections'], list):
            raise ValueError("collections must be a list")
        
        for collection in params['collections']:
            if not isinstance(collection, str):
                raise ValueError("collection IDs must be strings")
    
    # Validate limit
    if 'limit' in params:
        limit = params['limit']
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        
        if limit > 10000:
            raise ValueError("limit too large (max 10000)")
    
    return True


def validate_auth_token(token):
    """
    Basic validation for authentication token.
    
    Parameters
    ----------
    token : str
        Authentication token
        
    Returns
    -------
    bool
        True if token appears valid
    """
    if not token or not isinstance(token, str):
        return False
        
    # Basic checks
    if len(token.strip()) < 10:
        return False
        
    return True


def validate_datetime_format(datetime_str):
    """
    Validate datetime string format.
    
    Parameters
    ----------
    datetime_str : str
        Datetime string to validate
        
    Returns
    -------
    bool
        True if valid format
    """
    import re
    
    # RFC3339 datetime patterns
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$',
        r'^\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}$',
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, datetime_str):
            return True
    
    return False
