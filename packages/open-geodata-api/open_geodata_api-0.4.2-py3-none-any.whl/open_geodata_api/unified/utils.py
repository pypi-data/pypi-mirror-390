"""
Utility functions for Unified STAC Client
"""

from typing import Dict, Optional


def create_band_mapping():
    """
    Create comprehensive band mapping for different naming conventions.
    
    Returns
    -------
    dict
        Band mapping dictionary
    """
    return {
        # Standard Sentinel-2 bands to common names
        'B01': 'coastal',
        'B02': 'blue',
        'B03': 'green',
        'B04': 'red',
        'B05': 'rededge1',
        'B06': 'rededge2',
        'B07': 'rededge3',
        'B08': 'nir',
        'B8A': 'nir08',
        'B09': 'nir09',
        'B11': 'swir16',
        'B12': 'swir22',
        
        # Quality bands
        'SCL': 'scl',
        'AOT': 'aot',
        'WVP': 'wvp',
        
        # Alternative naming
        'NIR': 'nir',
        'SWIR1': 'swir16',
        'SWIR2': 'swir22',
        'BLUE': 'blue',
        'GREEN': 'green',
        'RED': 'red',
    }


def map_band_names(band_name, prefer_jp2=True):
    """
    Map band names to different conventions.
    
    Parameters
    ----------
    band_name : str
        Original band name
    prefer_jp2 : bool, default True
        Whether to prefer JP2 format assets
        
    Returns
    -------
    str or None
        Mapped band name
    """
    band_mapping = create_band_mapping()
    
    # Normalize input
    band_key = band_name.upper().strip()
    
    # Direct mapping
    if band_key in band_mapping:
        mapped = band_mapping[band_key]
        if prefer_jp2:
            return "{}-jp2".format(mapped)
        return mapped
    
    # Reverse mapping (common name to standard)
    reverse_mapping = {v: k for k, v in band_mapping.items()}
    if band_name.lower() in reverse_mapping:
        return reverse_mapping[band_name.lower()]
    
    return None


def normalize_datetime(datetime_str):
    """
    Normalize datetime string to RFC3339 format.
    
    Parameters
    ----------
    datetime_str : str
        Input datetime string
        
    Returns
    -------
    str
        Normalized datetime string
    """
    if not datetime_str:
        return datetime_str
        
    # Simple date format (YYYY-MM-DD)
    if len(datetime_str) == 10 and '-' in datetime_str:
        return "{}T00:00:00Z".format(datetime_str)
    
    # Date range format (YYYY-MM-DD/YYYY-MM-DD)  
    if '/' in datetime_str:
        parts = datetime_str.split('/')
        if len(parts) == 2:
            start, end = parts
            if len(start) == 10 and len(end) == 10:
                return "{}T00:00:00Z/{}T23:59:59Z".format(start, end)
    
    # Already in proper format - return as is
    return datetime_str


def extract_collection_metadata(collection_data):
    """
    Extract useful metadata from a STAC collection.
    
    Parameters
    ----------
    collection_data : dict
        Raw collection data from API
        
    Returns
    -------
    dict
        Simplified collection metadata
    """
    return {
        'id': collection_data.get('id'),
        'title': collection_data.get('title', ''),
        'description': collection_data.get('description', ''),
        'license': collection_data.get('license', ''),
        'extent': collection_data.get('extent', {}),
        'item_assets': collection_data.get('item_assets', {}),
        'providers': [p.get('name') for p in collection_data.get('providers', [])],
        'keywords': collection_data.get('keywords', [])
    }


def create_asset_summary(item_data):
    """
    Create summary of available assets in a STAC item.
    
    Parameters
    ----------
    item_data : dict
        STAC item data
        
    Returns
    -------
    dict
        Asset summary
    """
    assets = item_data.get('assets', {})
    
    summary = {
        'total_assets': len(assets),
        'asset_keys': list(assets.keys()),
        'asset_types': set(),
        'formats': set(),
        'bands': []
    }
    
    for key, asset in assets.items():
        # Get asset type
        asset_type = asset.get('type', 'unknown')
        summary['asset_types'].add(asset_type)
        
        # Get format from href extension or type
        href = asset.get('href', '')
        if href:
            ext = href.split('.')[-1].lower()
            summary['formats'].add(ext)
        
        # Check if it's a band asset
        band_indicators = ['b0', 'b1', 'blue', 'red', 'green', 'nir']
        if any(indicator in key.lower() for indicator in band_indicators):
            summary['bands'].append(key)
    
    # Convert sets to lists for JSON serialization
    summary['asset_types'] = list(summary['asset_types'])
    summary['formats'] = list(summary['formats'])
    
    return summary


def detect_auth_requirement(api_url):
    """
    Attempt to detect if an API requires authentication.
    
    Parameters
    ----------
    api_url : str
        API URL to test
        
    Returns
    -------
    bool
        True if authentication appears to be required
    """
    import requests
    
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 401:
            return True
        elif response.status_code == 403:
            return True
        elif response.status_code == 200:
            try:
                data = response.json()
                content_str = str(data).lower()
                auth_indicators = ['authentication', 'unauthorized', 'api key', 'token']
                if any(indicator in content_str for indicator in auth_indicators):
                    return True
            except (ValueError, TypeError):
                pass
            
            return False
        else:
            return False
            
    except requests.RequestException:
        return False
