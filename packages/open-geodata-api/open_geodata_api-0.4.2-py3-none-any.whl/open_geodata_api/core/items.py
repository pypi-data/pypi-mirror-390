"""
Core STAC Item class - focused on URL access and metadata
"""

from typing import Dict, Any, Optional, List

from .assets import STACAssets

class STACItem:
    """Universal STAC Item wrapper - focused on URL access and flexibility."""
    
    def __init__(self, item_data: Dict, provider: str = "unknown"):
        self._data = item_data.copy()
        self.provider = provider
        self.assets = STACAssets(self._data.get('assets', {}))
        self.properties = self._data.get('properties', {})
        self.geometry = self._data.get('geometry', {})
        self.bbox = self._data.get('bbox', [])
        self.id = self._data.get('id', '')
        self.collection = self._data.get('collection', '')
        self.type = self._data.get('type', 'Feature')
        self.stac_version = self._data.get('stac_version', '')
        self.links = self._data.get('links', [])
    
    def __getitem__(self, key):
        return self._data[key]
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def to_dict(self):
        return self._data.copy()
    
    def copy(self):
        return STACItem(self._data.copy(), provider=self.provider)
    
    def get_asset_url(self, asset_key: str, signed: Optional[bool] = None) -> str:
        """Get ready-to-use asset URL with automatic provider handling."""
        if asset_key not in self.assets:
            available_assets = list(self.assets.keys())
            raise KeyError(f"Asset '{asset_key}' not found. Available assets: {available_assets}")
        
        url = self.assets[asset_key].href
        
        # Auto-handle based on provider
        if signed is None:
            signed = (self.provider == "planetary_computer")
        
        if signed and self.provider == "planetary_computer":
            try:
                from ..planetary.signing import sign_url
                return sign_url(url)
            except ImportError:
                print("⚠️ planetary-computer package not found, returning unsigned URL")
                return url
        elif self.provider == "earthsearch":
            try:
                from ..earthsearch.validation import validate_url
                return validate_url(url)
            except ImportError:
                return url
        
        return url
    
    def get_all_asset_urls(self, signed: Optional[bool] = None) -> Dict[str, str]:
        """Get all asset URLs as a dictionary - ready for any raster package."""
        return {
            asset_key: self.get_asset_url(asset_key, signed=signed)
            for asset_key in self.assets.keys()
        }
    
    def get_assets_by_type(self, asset_type: str = "image/tiff", exact_match: bool = False) -> Dict[str, str]:
        """
        🔧 FIXED: Get URLs for assets of specific type with flexible matching.
        
        Args:
            asset_type: MIME type to search for (default: "image/tiff")
            exact_match: If True, requires exact string match. If False, uses substring matching.
            
        Returns:
            Dictionary of {asset_key: url} for matching assets
        """
        matching_assets = {}
        
        for asset_key, asset in self.assets.items():
            asset_mime_type = getattr(asset, 'type', '')
            
            if exact_match:
                # Exact match
                if asset_mime_type == asset_type:
                    matching_assets[asset_key] = self.get_asset_url(asset_key)
            else:
                # Flexible substring matching (default behavior)
                if asset_type.lower() in asset_mime_type.lower():
                    matching_assets[asset_key] = self.get_asset_url(asset_key)
        
        return matching_assets
    
    def get_raster_assets(self, signed: Optional[bool] = None) -> Dict[str, str]:
        """🆕 NEW: Get all raster/image assets (COGs, TIFFs, etc.)."""
        raster_types = ["image/tiff", "image/geotiff", "application/geotiff"]
        
        raster_assets = {}
        for asset_key, asset in self.assets.items():
            asset_type = getattr(asset, 'type', '').lower()
            if any(raster_type in asset_type for raster_type in raster_types):
                raster_assets[asset_key] = self.get_asset_url(asset_key, signed=signed)
        
        return raster_assets
    
    def get_metadata_assets(self) -> Dict[str, str]:
        """🆕 NEW: Get all metadata assets (XML, JSON, etc.)."""
        metadata_types = ["application/xml", "application/json", "text/xml"]
        
        metadata_assets = {}
        for asset_key, asset in self.assets.items():
            asset_type = getattr(asset, 'type', '').lower()
            if any(meta_type in asset_type for meta_type in metadata_types):
                metadata_assets[asset_key] = self.get_asset_url(asset_key)
        
        return metadata_assets
    
    def list_asset_types(self) -> Dict[str, List[str]]:
        """🆕 NEW: List all unique asset types and which assets have them."""
        type_mapping = {}
        
        for asset_key, asset in self.assets.items():
            asset_type = getattr(asset, 'type', 'unknown')
            if asset_type not in type_mapping:
                type_mapping[asset_type] = []
            type_mapping[asset_type].append(asset_key)
        
        return type_mapping
    
    def get_band_urls(self, bands: List[str], signed: Optional[bool] = None) -> Dict[str, str]:
        """Get URLs for specific bands/assets."""
        urls = {}
        missing_bands = []
        
        for band in bands:
            if band in self.assets:
                urls[band] = self.get_asset_url(band, signed=signed)
            else:
                missing_bands.append(band)
        
        if missing_bands:
            available_assets = list(self.assets.keys())
            print(f"⚠️ Bands not available: {missing_bands}")
            print(f"📊 Available assets: {available_assets}")
        
        return urls
    
    def list_assets(self) -> List[str]:
        """Return list of available asset keys."""
        return list(self.assets.keys())
    
    def has_asset(self, asset_key: str) -> bool:
        """Check if asset exists."""
        return asset_key in self.assets
    
    def get_rgb_urls(self, signed: Optional[bool] = None) -> Dict[str, str]:
        """Get RGB band URLs (convenience method)."""
        rgb_bands = ['B04', 'B03', 'B02']
        
        if self.provider == "planetary_computer":
            return self.get_band_urls(rgb_bands, signed=signed)
        elif self.provider == "earthsearch":
            # EarthSearch uses different band names
            rgb_bands = ['red', 'green', 'blue']
            return self.get_band_urls(rgb_bands, signed=signed)
        else:
            # Fallback to generic asset URLs
            return self.get_all_asset_urls(signed=signed)
    
    def get_sentinel2_urls(self, signed: Optional[bool] = None) -> Dict[str, str]:
        """Get common Sentinel-2 band URLs (convenience method)."""
        s2_bands = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B11', 'B12']
        es_bands = ['coastal', 'blue', 'green', 'red', 'rededge1', 'rededge2', 'rededge3', 'nir', 'nir08', 'nir09', 'swir16', 'swir22']
        
        available_assets = list(self.assets.keys())
        
        if any(band in available_assets for band in s2_bands):
            return self.get_band_urls(s2_bands, signed=signed)
        elif any(band in available_assets for band in es_bands):
            return self.get_band_urls(es_bands, signed=signed)
        else:
            return self.get_all_asset_urls(signed=signed)
    
    def print_assets_info(self):
        """🔧 ENHANCED: Print detailed information about all available assets including types."""
        print(f"📦 Item: {self.id}")
        print(f"🔗 Provider: {self.provider}")
        print(f"📅 Date: {self.properties.get('datetime', 'Unknown')}")
        print(f"☁️ Cloud Cover: {self.properties.get('eo:cloud_cover', 'N/A')}%")
        print(f"📊 Available Assets ({len(self.assets)}):")
        
        # Group assets by type for better display
        type_groups = self.list_asset_types()
        
        for asset_type, asset_keys in type_groups.items():
            print(f"\n📋 Type: {asset_type}")
            for asset_key in asset_keys:
                asset = self.assets[asset_key]
                print(f"   {asset_key:12s} | {asset.title}")
        
        print(f"\n💡 Usage Examples:")
        print(f"   # Get all image/TIFF assets:")
        print(f"   tiff_urls = item.get_assets_by_type('image/tiff')")
        print(f"   # Get all raster assets:")
        print(f"   raster_urls = item.get_raster_assets()")
        print(f"   # List asset types:")
        print(f"   types = item.list_asset_types()")
    
    def __repr__(self):
        return f"STACItem(id='{self.id}', collection='{self.collection}', provider='{self.provider}', assets={len(self.assets)})"
