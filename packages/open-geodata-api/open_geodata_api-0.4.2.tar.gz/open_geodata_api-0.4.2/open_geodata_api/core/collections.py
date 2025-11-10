"""
STAC Item Collections module - Complete with all essential functions including missing ones
"""

import re
import json
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime, timedelta

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

try:
    import geojson
    GEOJSON_AVAILABLE = True
except ImportError:
    GEOJSON_AVAILABLE = False

class STACItemCollection:
    """
    Complete STAC Item Collection with all essential functions including the missing ones.
    """
    
    def __init__(self, items: List[Dict], provider: str = "unknown"):
        """
        Initialize STAC Item Collection.
        
        Args:
            items: List of STAC item dictionaries
            provider: Provider name (e.g., "planetary_computer", "earthsearch")
        """
        self._items = items
        self.provider = provider
        self._cached_dataframe = None
        self._parent_search = None
    
    def __len__(self):
        """Return number of items in collection."""
        return len(self._items)
    
    def __getitem__(self, index):
        """Get item by index as STACItem object."""
        from .items import STACItem
        return STACItem(self._items[index], provider=self.provider)
    
    def __iter__(self):
        """Iterate over items as STACItem objects."""
        from .items import STACItem
        for item_data in self._items:
            yield STACItem(item_data, provider=self.provider)
    
    @property
    def items(self):
        """Get all items as list of STACItem objects."""
        from .items import STACItem
        return [STACItem(item_data, provider=self.provider) for item_data in self._items]
    
    @property
    def raw_items(self):
        """Get raw item dictionaries (for internal use)."""
        return self._items
    
    # ========================================
    # MISSING FUNCTIONS - ADDED
    # ========================================
    
    def get_available_bands(self) -> List[str]:
        """
        🆕 ADDED: Get list of all available bands/assets across the collection.
        
        Returns:
            Sorted list of unique band/asset names available in the collection
        """
        all_bands = set()
        
        for item in self._items:
            assets = item.get('assets', {})
            all_bands.update(assets.keys())
        
        return sorted(list(all_bands))
    
    def get_all_urls(self, signed: Optional[bool] = None) -> Dict[str, Dict[str, str]]:
        """
        🆕 ADDED: Get all URLs in the requested format.
        
        Format: {<product_id>: {<band_name>: <url>, <band_name>: <url>, ...}, ...}
        
        Args:
            signed: Whether to sign URLs (auto-detected by provider if None)
            
        Returns:
            Dictionary with product_id -> {band_name: url} mapping
        """
        all_urls = {}
        
        from .items import STACItem
        for i, item_data in enumerate(self._items):
            stac_item = STACItem(item_data, provider=self.provider)
            product_id = item_data.get('id', f'item_{i}')
            
            try:
                # Get all asset URLs for this item
                item_urls = stac_item.get_all_asset_urls(signed=signed)
                all_urls[product_id] = item_urls
                
            except Exception as e:
                print(f"⚠️ Error processing item {product_id}: {e}")
                all_urls[product_id] = {}
        
        return all_urls
    
    def get_band_urls(self, band_names: Optional[List[str]] = None, 
                      asset_type: str = "all", signed: Optional[bool] = None) -> Dict[str, Dict[str, str]]:
        """
        🆕 ADDED: Get URLs for specific bands or asset types with filtering options.
        
        Args:
            band_names: List of specific band names to include (None for all)
            asset_type: Filter by asset type:
                - "all": All assets (default)
                - "image": Only image/tiff assets
                - "bands": Only spectral bands (B01, B02, etc.)
                - "visual": Only visual/RGB assets
            signed: Whether to sign URLs (auto-detected by provider if None)
            
        Returns:
            Dictionary with product_id -> {band_name: url} mapping
        """
        filtered_urls = {}
        
        from .items import STACItem
        for i, item_data in enumerate(self._items):
            stac_item = STACItem(item_data, provider=self.provider)
            product_id = item_data.get('id', f'item_{i}')
            
            try:
                # Get all asset URLs for this item
                all_item_urls = stac_item.get_all_asset_urls(signed=signed)
                
                # Apply filtering
                filtered_item_urls = {}
                
                for asset_key, asset_url in all_item_urls.items():
                    # Check if asset should be included
                    include_asset = False
                    
                    # Filter by band names if specified
                    if band_names:
                        if asset_key in band_names:
                            include_asset = True
                    else:
                        # Filter by asset type
                        if asset_type == "all":
                            include_asset = True
                        elif asset_type == "image":
                            # Check if it's an image/tiff asset
                            asset_data = item_data.get('assets', {}).get(asset_key, {})
                            asset_mime_type = asset_data.get('type', '').lower()
                            if any(img_type in asset_mime_type for img_type in ['image/tiff', 'image/geotiff', 'application/geotiff']):
                                include_asset = True
                        elif asset_type == "bands":
                            # Check if it's a spectral band (B01, B02, etc.)
                            if re.match(r'^B\d+A?$', asset_key) or asset_key.lower() in ['red', 'green', 'blue', 'nir', 'swir']:
                                include_asset = True
                        elif asset_type == "visual":
                            # Check if it's a visual asset
                            if asset_key.lower() in ['visual', 'true-color', 'rgb', 'thumbnail', 'preview']:
                                include_asset = True
                    
                    if include_asset:
                        filtered_item_urls[asset_key] = asset_url
                
                filtered_urls[product_id] = filtered_item_urls
                
            except Exception as e:
                print(f"⚠️ Error processing item {product_id}: {e}")
                filtered_urls[product_id] = {}
        
        return filtered_urls
    
    # ========================================
    # UPDATED FUNCTIONS
    # ========================================
    
    def to_simple_products_list(self, include_urls: bool = True, 
                               url_bands: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        🔧 UPDATED: Convert collection to simple products list with optional URLs.
        
        Args:
            include_urls: Whether to include URLs with href key
            url_bands: Specific bands to include URLs for (None for all)
            
        Returns:
            List of simplified product dictionaries with optional URLs
        """
        simple_products = []
        
        from .items import STACItem
        for i, item_data in enumerate(self._items):
            properties = item_data.get('properties', {})
            
            simple_product = {
                'id': item_data.get('id', f'item_{i}'),
                'collection': item_data.get('collection', 'unknown'),
                'datetime': properties.get('datetime', 'unknown'),
                'cloud_cover': properties.get('eo:cloud_cover'),
                'asset_count': len(item_data.get('assets', {})),
                'provider': self.provider
            }
            
            # Add URLs if requested
            if include_urls:
                try:
                    stac_item = STACItem(item_data, provider=self.provider)
                    
                    if url_bands:
                        # Get URLs for specific bands
                        urls = {}
                        for band in url_bands:
                            if stac_item.has_asset(band):
                                urls[band] = stac_item.get_asset_url(band)
                        simple_product['href'] = urls
                    else:
                        # Get all URLs
                        simple_product['href'] = stac_item.get_all_asset_urls()
                        
                except Exception as e:
                    print(f"⚠️ Error getting URLs for item {simple_product['id']}: {e}")
                    simple_product['href'] = {}
            
            simple_products.append(simple_product)
        
        return simple_products
    
    # ========================================
    # EXISTING ESSENTIAL FUNCTIONS (MAINTAINED)
    # ========================================
    
    def to_list(self) -> List[Dict]:
        """Convert collection to list of dictionaries."""
        return self._items.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert collection to dictionary format."""
        return {
            'type': 'FeatureCollection',
            'provider': self.provider,
            'total_items': len(self._items),
            'features': self._items.copy(),
            'metadata': {
                'date_range': self.get_date_range(),
                'extensions': self.list_asset_extensions(),
                'collections': self.get_unique_collections(),
                'available_bands': self.get_available_bands()
            }
        }
    
    def to_geojson(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Convert collection to GeoJSON format."""
        if GEOJSON_AVAILABLE:
            try:
                features = []
                for item in self._items:
                    if item.get('geometry'):
                        features.append(geojson.Feature(
                            geometry=item['geometry'],
                            properties=item.get('properties', {}),
                            id=item.get('id')
                        ))
                
                collection = geojson.FeatureCollection(features)
                
                if filename:
                    with open(filename, 'w') as f:
                        geojson.dump(collection, f, indent=2)
                    print(f"✅ GeoJSON saved to {filename}")
                
                return collection
                
            except Exception as e:
                print(f"⚠️ geojson library error: {e}, falling back to manual creation")
        
        # Manual GeoJSON creation
        geojson_data = {
            'type': 'FeatureCollection',
            'features': []
        }
        
        for item in self._items:
            if item.get('geometry'):
                feature = {
                    'type': 'Feature',
                    'geometry': item['geometry'],
                    'properties': item.get('properties', {}),
                    'id': item.get('id')
                }
                geojson_data['features'].append(feature)
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(geojson_data, f, indent=2)
            print(f"✅ GeoJSON saved to {filename}")
        
        if not GEOJSON_AVAILABLE:
            print("💡 For better GeoJSON support, install: pip install geojson")
        
        return geojson_data
    
    def get_all_assets(self) -> Dict[str, List[str]]:
        """Get all unique assets across all items."""
        all_assets = {}
        
        for i, item in enumerate(self._items):
            assets = item.get('assets', {})
            item_id = item.get('id', f'item_{i}')
            
            for asset_key in assets.keys():
                if asset_key not in all_assets:
                    all_assets[asset_key] = []
                all_assets[asset_key].append(item_id)
        
        return all_assets
    
    def get_assets_by_collection(self) -> Dict[str, List[str]]:
        """Get assets grouped by collection."""
        collection_assets = {}
        
        for item in self._items:
            collection = item.get('collection', 'unknown')
            assets = list(item.get('assets', {}).keys())
            
            if collection not in collection_assets:
                collection_assets[collection] = set()
            
            collection_assets[collection].update(assets)
        
        return {
            collection: sorted(list(assets)) 
            for collection, assets in collection_assets.items()
        }
    
    def to_products_dict(self) -> Dict[str, Dict[str, Any]]:
        """Convert collection to products dictionary with detailed metadata."""
        products = {}
        
        for i, item in enumerate(self._items):
            item_id = item.get('id', f'item_{i}')
            properties = item.get('properties', {})
            assets = item.get('assets', {})
            
            products[item_id] = {
                'id': item_id,
                'collection': item.get('collection', 'unknown'),
                'datetime': properties.get('datetime', 'unknown'),
                'cloud_cover': properties.get('eo:cloud_cover'),
                'geometry': item.get('geometry'),
                'bbox': item.get('bbox'),
                'assets': list(assets.keys()),
                'asset_count': len(assets),
                'provider': self.provider,
                'properties': properties
            }
        
        return products
    
    def get_common_bands(self, min_occurrence: float = 0.5) -> List[str]:
        """Get commonly available bands/assets across the collection."""
        if not self._items:
            return []
        
        asset_counts = {}
        total_items = len(self._items)
        
        for item in self._items:
            assets = item.get('assets', {})
            for asset_key in assets.keys():
                asset_counts[asset_key] = asset_counts.get(asset_key, 0) + 1
        
        min_count = int(total_items * min_occurrence)
        common_bands = [
            asset for asset, count in asset_counts.items() 
            if count >= min_count
        ]
        
        return sorted(common_bands)
    
    # ========================================
    # PATTERN MATCHING AND FILTERING
    # ========================================
    
    def get_assets_by_pattern(self, pattern: str, match_type: str = "extension") -> List[str]:
        """Get asset names that match the specified pattern."""
        matching_assets = []
        
        for item in self._items:
            assets = item.get('assets', {})
            
            for asset_key, asset_data in assets.items():
                if self._asset_matches_pattern(asset_key, asset_data, pattern, match_type):
                    if asset_key not in matching_assets:
                        matching_assets.append(asset_key)
        
        return matching_assets
    
    def _asset_matches_pattern(self, asset_key: str, asset_data: Dict, 
                              pattern: str, match_type: str) -> bool:
        """Check if an asset matches the specified pattern."""
        pattern_lower = pattern.lower()
        
        if match_type == "extension":
            return self._check_extension_match(asset_data, pattern_lower)
        elif match_type == "mime":
            return self._check_mime_match(asset_data, pattern_lower)
        elif match_type == "name":
            return pattern_lower in asset_key.lower()
        elif match_type == "url":
            asset_url = asset_data.get('href', '')
            return pattern_lower in asset_url.lower()
        else:
            return self._check_extension_match(asset_data, pattern_lower)
    
    def _check_extension_match(self, asset_data: Dict, pattern: str) -> bool:
        """Check if asset's actual file extension matches pattern."""
        asset_url = asset_data.get('href', '')
        if not asset_url:
            return False
        
        try:
            parsed_url = urlparse(asset_url)
            url_path = parsed_url.path
            file_extension = Path(url_path).suffix.lower()
            pattern_clean = pattern.lstrip('.')
            extension_clean = file_extension.lstrip('.')
            return extension_clean == pattern_clean or pattern in file_extension
        except Exception:
            return False
    
    def _check_mime_match(self, asset_data: Dict, pattern: str) -> bool:
        """Check if asset's MIME type matches pattern."""
        asset_type = asset_data.get('type', '').lower()
        return pattern in asset_type
    
    def get_assets_by_extension(self, extension: str) -> List[str]:
        """Convenience method to get assets by file extension."""
        if not extension.startswith('.'):
            extension = '.' + extension
        return self.get_assets_by_pattern(extension, match_type="extension")
    
    def get_assets_by_mime_type(self, mime_type: str) -> List[str]:
        """Convenience method to get assets by MIME type."""
        return self.get_assets_by_pattern(mime_type, match_type="mime")
    
    def list_asset_extensions(self) -> Dict[str, List[str]]:
        """List all unique file extensions and which assets have them."""
        extensions_map = {}
        
        for item in self._items:
            assets = item.get('assets', {})
            
            for asset_key, asset_data in assets.items():
                asset_url = asset_data.get('href', '')
                if asset_url:
                    try:
                        parsed_url = urlparse(asset_url)
                        file_extension = Path(parsed_url.path).suffix.lower()
                        
                        if file_extension:
                            if file_extension not in extensions_map:
                                extensions_map[file_extension] = []
                            if asset_key not in extensions_map[file_extension]:
                                extensions_map[file_extension].append(asset_key)
                    except Exception:
                        continue
        
        return extensions_map
    
    # ========================================
    # FILTERING FUNCTIONS
    # ========================================
    
    def filter_by_cloud_cover(self, max_cloud_cover: float) -> 'STACItemCollection':
        """Filter items by cloud cover percentage."""
        filtered_items = []
        
        for item in self._items:
            cloud_cover = item.get('properties', {}).get('eo:cloud_cover', 0)
            if cloud_cover <= max_cloud_cover:
                filtered_items.append(item)
        
        return STACItemCollection(filtered_items, provider=self.provider)
    
    def filter_by_date_range(self, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None, 
                        days_back: Optional[int] = None,
                        auto_fix_dates: bool = True) -> 'STACItemCollection':
        """
        🔧 ENHANCED: Filter items by date range with automatic invalid date correction.
        
        Args:
            start_date: Start date (YYYY-MM-DD format) - optional if using days_back
            end_date: End date (YYYY-MM-DD format) - optional if using days_back  
            days_back: Number of days back from today - alternative to start_date/end_date
            auto_fix_dates: Whether to automatically fix invalid dates (default: True)
            
        Returns:
            New STACItemCollection with filtered items
            
        Examples:
            # Using date range with auto-correction
            filtered = collection.filter_by_date_range("2024-01-01", "2024-02-31")  # Auto-fixes to 2024-02-29
            
            # Using days back (last 30 days)
            filtered = collection.filter_by_date_range(days_back=30)
            
            # Disable auto-correction
            filtered = collection.filter_by_date_range("2024-01-01", "2024-02-31", auto_fix_dates=False)
        """
        
        # Validate input parameters
        if not start_date and not end_date and not days_back:
            print("⚠️ No filtering parameters provided. Returning original collection.")
            return STACItemCollection(self._items.copy(), provider=self.provider)
        
        # Calculate date range based on parameters
        try:
            if days_back is not None:
                # Option 1: Use days_back parameter
                if start_date:
                    # days_back from specific start_date
                    start_dt = self._parse_date(start_date)
                    end_dt = start_dt + timedelta(days=days_back)
                else:
                    # days_back from today
                    end_dt = datetime.now()
                    start_dt = end_dt - timedelta(days=days_back)
            else:
                # Option 2: Use start_date and end_date
                start_dt = self._parse_date(start_date) if start_date else datetime.min
                end_dt = self._parse_date(end_date) if end_date else datetime.max
            
            # Convert to date objects for comparison
            start_date_obj = start_dt.date()
            end_date_obj = end_dt.date()
            
            print(f"🗓️ Filtering items from {start_date_obj} to {end_date_obj}")
            
        except ValueError as e:
            if auto_fix_dates:
                print(f"❌ Date parsing error: {e}")
                print("💡 Use YYYY-MM-DD format for dates or set auto_fix_dates=True")
            else:
                print(f"❌ Date parsing error with auto_fix_dates=False: {e}")
            return STACItemCollection([], provider=self.provider)
        
        # Filter items
        filtered_items = []
        processed_items = 0
        
        for item in self._items:
            item_datetime = item.get('properties', {}).get('datetime', '')
            if item_datetime:
                try:
                    # Parse item datetime
                    item_dt = self._parse_item_datetime(item_datetime)
                    item_date = item_dt.date()
                    
                    # Check if item falls within date range
                    if start_date_obj <= item_date <= end_date_obj:
                        filtered_items.append(item)
                    
                    processed_items += 1
                    
                except Exception as e:
                    # Skip items with invalid datetime
                    continue
        
        print(f"✅ Filtered {len(filtered_items)} items from {processed_items} total items")
        
        return STACItemCollection(filtered_items, provider=self.provider)
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        🔧 FIXED: Parse date string with automatic invalid date correction.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            datetime object with corrected date if needed
            
        Raises:
            ValueError: If date string format or month is invalid
        """
        import calendar
        import re
        
        if not date_str:
            raise ValueError("Date string cannot be empty")
        
        # First try direct parsing for valid dates
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d', 
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If direct parsing fails, try to fix invalid dates
        try:
            # Handle YYYY-MM-DD format with potential invalid day
            match = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", date_str)
            if match:
                year, month, day = map(int, match.groups())
                
                # Validate month
                if month < 1 or month > 12:
                    raise ValueError(f"Invalid month: {month}. Must be 1-12.")
                
                # Get last valid day of the month
                last_day = calendar.monthrange(year, month)[1]
                
                if day > last_day:
                    print(f"⚠️ Invalid date {date_str}: Day {day} doesn't exist in {calendar.month_name[month]} {year}")
                    print(f"🔧 Auto-correcting to {year}-{month:02d}-{last_day:02d}")
                    day = last_day
                
                return datetime(year, month, day)
        
        except Exception:
            pass
        
        # Try pandas if available as last resort
        if PANDAS_AVAILABLE:
            try:
                return pd.to_datetime(date_str).to_pydatetime()
            except Exception:
                pass
        
        raise ValueError(f"Unable to parse date: '{date_str}'. Use YYYY-MM-DD format.")
    
    def _parse_item_datetime(self, datetime_str: str) -> datetime:
        """Parse item datetime with robust error handling."""
        if PANDAS_AVAILABLE:
            try:
                return pd.to_datetime(datetime_str).to_pydatetime()
            except Exception:
                pass
        
        datetime_formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d'
        ]
        
        for fmt in datetime_formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse item datetime: '{datetime_str}'")
    
    def get_unique_collections(self) -> List[str]:
        """Get list of unique collection names."""
        collections = set()
        for item in self._items:
            collection = item.get('collection', '')
            if collection:
                collections.add(collection)
        return list(collections)
    
    def get_date_range(self) -> Dict[str, str]:
        """Get date range of items in collection."""
        dates = []
        for item in self._items:
            item_datetime = item.get('properties', {}).get('datetime', '')
            if item_datetime:
                try:
                    dates.append(self._parse_item_datetime(item_datetime))
                except Exception:
                    continue
        
        if dates:
            return {
                'start': min(dates).strftime('%Y-%m-%d'),
                'end': max(dates).strftime('%Y-%m-%d')
            }
        
        return {'start': 'unknown', 'end': 'unknown'}
    
    # ========================================
    # PANDAS/GEOPANDAS DEPENDENT FUNCTIONS
    # ========================================
    
    def to_dataframe(self, include_geometry: bool = True) -> 'pd.DataFrame':
        """Convert collection to pandas/geopandas DataFrame."""
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "❌ pandas is required for to_dataframe().\n"
                "💡 Install with: pip install pandas"
            )
        
        if self._cached_dataframe is not None:
            return self._cached_dataframe
        
        # Build DataFrame from items
        df_data = []
        for item in self._items:
            row = {
                'id': item.get('id', ''),
                'collection': item.get('collection', ''),
                'datetime': item.get('properties', {}).get('datetime', ''),
                'provider': self.provider
            }
            
            # Add all properties
            properties = item.get('properties', {})
            for key, value in properties.items():
                if key not in row:
                    row[key] = value
            
            # Add geometry info
            geometry = item.get('geometry', {})
            if geometry:
                row['geometry_type'] = geometry.get('type', '')
                
            # Add bbox if available
            bbox = item.get('bbox', [])
            if bbox and len(bbox) >= 4:
                row['bbox_west'] = bbox[0]
                row['bbox_south'] = bbox[1]
                row['bbox_east'] = bbox[2]
                row['bbox_north'] = bbox[3]
            
            # Add asset count
            assets = item.get('assets', {})
            row['asset_count'] = len(assets)
            
            df_data.append(row)
        
        # Create DataFrame
        if include_geometry and GEOPANDAS_AVAILABLE:
            try:
                from shapely.geometry import shape
                
                geometries = []
                for item in self._items:
                    geom = item.get('geometry')
                    if geom:
                        geometries.append(shape(geom))
                    else:
                        geometries.append(None)
                
                df = gpd.GeoDataFrame(df_data, geometry=geometries)
            except Exception:
                df = pd.DataFrame(df_data)
                if include_geometry:
                    print("⚠️ Failed to create GeoDataFrame, falling back to regular DataFrame")
        else:
            df = pd.DataFrame(df_data)
            if include_geometry and not GEOPANDAS_AVAILABLE:
                print("💡 For geometry support, install: pip install geopandas")
        
        self._cached_dataframe = df
        return df
    
    def to_geodataframe(self) -> 'gpd.GeoDataFrame':
        """Convert collection to geopandas GeoDataFrame."""
        if not GEOPANDAS_AVAILABLE:
            raise ImportError(
                "❌ geopandas is required for to_geodataframe().\n"
                "💡 Install with: pip install geopandas"
            )
        
        return self.to_dataframe(include_geometry=True)
    
    # ========================================
    # EXPORT AND UTILITY FUNCTIONS
    # ========================================
    
    def export_urls_json(self, filename: str, asset_keys: Optional[List[str]] = None):
        """Export all URLs to JSON file for external processing."""
        all_urls = {}
        processed_count = 0
        
        from .items import STACItem
        for item in self._items:
            stac_item = STACItem(item, provider=self.provider)
            item_id = item.get('id', f'item_{processed_count}')
            
            try:
                if asset_keys:
                    item_urls = {}
                    for asset_key in asset_keys:
                        if stac_item.has_asset(asset_key):
                            item_urls[asset_key] = stac_item.get_asset_url(asset_key)
                    all_urls[item_id] = item_urls
                else:
                    all_urls[item_id] = stac_item.get_all_asset_urls()
                
                processed_count += 1
            except Exception as e:
                print(f"⚠️ Error processing item {item_id}: {e}")
                continue
        
        export_data = {
            'provider': self.provider,
            'total_items': len(self._items),
            'processed_items': processed_count,
            'exported_at': datetime.now().isoformat(),
            'asset_keys': asset_keys or 'all',
            'urls': all_urls
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Exported {processed_count} items to {filename}")
    
    def print_collection_summary(self):
        """Print a comprehensive summary of the collection."""
        date_range = self.get_date_range()
        extensions = self.list_asset_extensions()
        common_bands = self.get_common_bands()
        available_bands = self.get_available_bands()
        
        print(f"📦 STAC Collection Summary")
        print(f"=" * 50)
        print(f"🔗 Provider: {self.provider}")
        print(f"📊 Total Items: {len(self._items)}")
        print(f"📅 Date Range: {date_range['start']} to {date_range['end']}")
        print(f"📋 Collections: {self.get_unique_collections()}")
        print(f"🎯 Available Bands ({len(available_bands)}): {available_bands[:10]}{'...' if len(available_bands) > 10 else ''}")
        print(f"🔗 Common Bands: {common_bands[:10]}{'...' if len(common_bands) > 10 else ''}")
        
        print(f"\n📋 File Extensions:")
        for ext, assets in list(extensions.items())[:5]:
            print(f"  {ext}: {len(assets)} assets")
        
        print(f"\n💡 Usage Examples:")
        print(f"  # Get available bands: bands = collection.get_available_bands()")
        print(f"  # Get all URLs: urls = collection.get_all_urls()")
        print(f"  # Get band URLs: urls = collection.get_band_urls(['B04', 'B03', 'B02'])")
        print(f"  # Get image URLs: urls = collection.get_band_urls(asset_type='image')")
        print(f"  # Simple products: products = collection.to_simple_products_list(include_urls=True)")
        
        # Show dependency status
        print(f"\n📦 Optional Dependencies:")
        print(f"  pandas: {'✅ Available' if PANDAS_AVAILABLE else '❌ Not installed (pip install pandas)'}")
        print(f"  geopandas: {'✅ Available' if GEOPANDAS_AVAILABLE else '❌ Not installed (pip install geopandas)'}")
        print(f"  geojson: {'✅ Available' if GEOJSON_AVAILABLE else '❌ Not installed (pip install geojson)'}")
    
    def check_dependencies(self):
        """Check status of optional dependencies."""
        deps = {
            'pandas': PANDAS_AVAILABLE,
            'geopandas': GEOPANDAS_AVAILABLE,
            'geojson': GEOJSON_AVAILABLE
        }
        
        print("📦 Dependency Status:")
        for dep, available in deps.items():
            status = "✅ Available" if available else "❌ Not installed"
            install_cmd = f"pip install {dep}" if not available else ""
            print(f"  {dep}: {status} {install_cmd}")
        
        return deps
    
    def __repr__(self):
        """String representation of the collection."""
        return f"STACItemCollection({len(self._items)} items, provider='{self.provider}')"
    
    def __str__(self):
        """Human-readable string representation."""
        stats = self.get_date_range()
        return f"STACItemCollection: {len(self._items)} items from {self.provider} ({stats['start']} to {stats['end']})"
