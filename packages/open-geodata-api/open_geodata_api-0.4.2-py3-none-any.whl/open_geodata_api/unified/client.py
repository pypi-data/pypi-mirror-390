"""
Unified STAC API Client

A flexible client that can connect to any STAC-compliant API endpoint
with optional authentication and consistent interface.
"""

from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
import requests
import json
from datetime import datetime, date

# Updated imports based on your project structure
from ..core.base_client import BaseSTACClient
from ..core.search import STACSearch
from ..core.items import STACItem
from ..core.collections import STACItemCollection
from .validation import validate_stac_endpoint, validate_search_params
from .utils import create_band_mapping, map_band_names, normalize_datetime


class UnifiedSTACClient(BaseSTACClient):
    """
    A unified client for connecting to any STAC API endpoint with flexible authentication.
    
    This client provides a consistent interface for accessing various STAC-compliant APIs
    while handling endpoint-specific differences and optional authentication.
    
    Parameters
    ----------
    api_url : str
        Base URL of the STAC API endpoint
    auth_token : str, optional
        Authentication token if required by the API
    headers : dict, optional
        Additional headers to include in requests
    timeout : int, default 30
        Request timeout in seconds
    verify_ssl : bool, default True
        Whether to verify SSL certificates
    """
    
    def __init__(
        self, 
        api_url,
        auth_token=None,
        headers=None,
        timeout=30,
        verify_ssl=True
    ):
        self.api_url = api_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.authenticated = bool(auth_token)
        
        # Setup session with optional authentication
        self.session = requests.Session()
        
        # Add custom headers if provided
        if headers:
            self.session.headers.update(headers)
            
        # Add authentication header only if token is provided
        if auth_token:
            self.session.headers.update({
                'Authorization': 'Bearer {}'.format(auth_token)
            })
            
        # Validate endpoint and get capabilities
        self._validate_and_setup()
        
        # Call parent init if needed
        try:
            super(UnifiedSTACClient, self).__init__()
        except TypeError:
            # Parent doesn't need arguments
            pass
        
    def _validate_and_setup(self):
        """Validate STAC endpoint and setup client capabilities."""
        try:
            # Get root catalog
            response = self.session.get(
                self.api_url, 
                timeout=self.timeout, 
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            self.root_catalog = response.json()
            self.stac_version = self.root_catalog.get('stac_version', 'unknown')
            
            # Discover search endpoint
            self.search_endpoint = None
            for link in self.root_catalog.get('links', []):
                if link.get('rel') == 'search':
                    self.search_endpoint = urljoin(self.api_url, link['href'])
                    break
            
            # Fallback to default search endpoint
            if not self.search_endpoint:
                self.search_endpoint = "{}/search".format(self.api_url)
                
            # Validate search endpoint
            try:
                validate_stac_endpoint(self.search_endpoint, self.session)
                self.search_available = True
            except Exception:
                self.search_available = False
                
        except Exception as e:
            raise ConnectionError("Failed to connect to STAC API at {}: {}".format(self.api_url, e))
    
    def _create_pystac_catalog_fallback(self):
        """
        Create a PySTAC catalog fallback for compatibility with BaseSTACClient.
        
        Returns
        -------
        pystac.Catalog or None
            PySTAC catalog object if possible, None otherwise
        """
        try:
            import pystac
            
            # Create a basic catalog from root
            catalog = pystac.Catalog(
                id=self.root_catalog.get('id', 'unified-catalog'),
                description=self.root_catalog.get('description', 'Unified STAC Catalog'),
                title=self.root_catalog.get('title', 'Unified Catalog')
            )
            
            return catalog
            
        except (ImportError, Exception):
            return None
    
    def search(
        self,
        collections=None,
        bbox=None,
        datetime=None,
        query=None,
        limit=100,
        **kwargs
    ):
        """
        Search for STAC items.
        
        Parameters
        ----------
        collections : list of str, optional
            Collection IDs to search
        bbox : list of float, optional
            Bounding box [west, south, east, north]
        datetime : str, optional
            Datetime range in RFC3339 format
        query : dict, optional
            Additional query parameters
        limit : int, default 100
            Maximum number of items to return
        **kwargs
            Additional search parameters
            
        Returns
        -------
        STACSearch
            Search results object
        """
        if not self.search_available:
            raise RuntimeError("Search endpoint not available for this STAC API")
            
        # Build search parameters
        search_params = {
            'limit': limit
        }
        
        if collections:
            search_params['collections'] = collections
        if bbox:
            search_params['bbox'] = bbox
        if datetime:
            search_params['datetime'] = normalize_datetime(datetime)
        if query:
            search_params['query'] = query
            
        # Add any additional parameters
        search_params.update(kwargs)
        
        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        # Validate parameters
        validate_search_params(search_params)
        
        try:
            # Execute search
            response = self.session.post(
                self.search_endpoint,
                json=search_params,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            search_results = response.json()
            
            # Convert to STACSearch object
            return self._create_search_object(search_results, search_params)
            
        except Exception as e:
            raise RuntimeError("Search failed: {}".format(e))
    
    def get_collections(self):
        """
        Get list of available collections.
        
        Returns
        -------
        list of dict
            Collection metadata
        """
        try:
            collections_url = "{}/collections".format(self.api_url)
            response = self.session.get(
                collections_url,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            collections_data = response.json()
            return collections_data.get('collections', [])
            
        except Exception as e:
            raise RuntimeError("Failed to get collections: {}".format(e))
    
    def list_collections(self):
        """
        Get list of collection IDs.
        
        Returns
        -------
        list of str
            Collection ID strings
        """
        collections = self.get_collections()
        return [col.get('id') for col in collections if col.get('id')]
    
    def get_collection_info(self, collection_id):
        """
        Get detailed information about a specific collection.
        
        Parameters
        ----------
        collection_id : str
            Collection ID
            
        Returns
        -------
        dict
            Collection metadata
        """
        try:
            collection_url = "{}/collections/{}".format(self.api_url, collection_id)
            response = self.session.get(
                collection_url,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            raise RuntimeError("Failed to get collection info for {}: {}".format(collection_id, e))
    
    def _create_search_object(self, search_results, search_params):
        """Create STACSearch object from API response."""
        items = []
        for feature in search_results.get('features', []):
            # Create STACItem
            stac_item = STACItem(feature)
            stac_item._client = self
            items.append(stac_item)
        
        # Create STACItemCollection
        item_collection = STACItemCollection(items)
        
        # Create STACSearch object
        search_obj = STACSearch(
            items=item_collection,
            search_params=search_params
        )
        
        # Add total results if available
        if 'numberMatched' in search_results:
            search_obj.total_results = search_results['numberMatched']
        
        return search_obj
    
    def get_asset_url(self, item, asset_key, prefer_jp2=True):
        """
        Get asset URL for a specific asset key, with band name mapping.
        
        Parameters
        ----------
        item : STACItem
            STAC item object
        asset_key : str
            Asset key (e.g., 'B02', 'blue', 'red')
        prefer_jp2 : bool, default True
            Prefer JP2 format assets if available
            
        Returns
        -------
        str or None
            Asset URL if found
        """
        # Map band names to common formats
        mapped_key = map_band_names(asset_key, prefer_jp2)
        
        # Get assets from item
        if hasattr(item, 'assets'):
            assets = item.assets
        else:
            assets = item.get('assets', {})
        
        # Try original key first
        if asset_key in assets:
            asset = assets[asset_key]
            if isinstance(asset, dict):
                return asset.get('href')
            elif hasattr(asset, 'href'):
                return asset.href
        
        # Try mapped key
        if mapped_key and mapped_key in assets:
            asset = assets[mapped_key]
            if isinstance(asset, dict):
                return asset.get('href')
            elif hasattr(asset, 'href'):
                return asset.href
        
        # Try variations
        variations = [
            asset_key.lower(),
            asset_key.upper(),
            "{}-jp2".format(asset_key) if prefer_jp2 else asset_key,
        ]
        
        for var in variations:
            if var in assets:
                asset = assets[var]
                if isinstance(asset, dict):
                    return asset.get('href')
                elif hasattr(asset, 'href'):
                    return asset.href
        
        return None
    
    def get_info(self):
        """
        Get client and endpoint information.
        
        Returns
        -------
        dict
            Client information
        """
        return {
            'client_type': 'UnifiedSTAC',
            'api_url': self.api_url,
            'stac_version': self.stac_version,
            'search_endpoint': self.search_endpoint,
            'search_available': self.search_available,
            'authenticated': self.authenticated,
            'collections_count': len(self.list_collections()),
        }


def create_unified_client(api_url, **kwargs):
    """
    Factory function to create a UnifiedSTACClient.
    
    Parameters
    ----------
    api_url : str
        STAC API endpoint URL
    **kwargs
        Additional client parameters
        
    Returns
    -------
    UnifiedSTACClient
        Configured client instance
    """
    return UnifiedSTACClient(api_url, **kwargs)
