"""
STAC Search with optimized 3-tier fallback strategy - Performance Enhanced
"""

import warnings
from typing import Dict, Optional, Any, List, Union
from .collections import STACItemCollection

try:
    import pystac_client
    import planetary_computer
    PYSTAC_AVAILABLE = True
except ImportError:
    PYSTAC_AVAILABLE = False

class STACSearch:
    """Optimized STAC Search with smart fallback strategy and improved performance."""
    
    def __init__(self, search_results: Dict, provider: str = "unknown",
                 client_instance=None, original_search_params: Optional[Dict] = None,
                 search_url: str = None, verbose: bool = False):
        
        self._results = search_results
        self._items = search_results.get('items', search_results.get('features', []))
        self.provider = provider
        self._client = client_instance
        self._original_params = original_search_params or {}
        self._search_url = search_url
        self._verbose = verbose
        
        # Optimized fallback strategy tracking
        self._fallback_attempted = False
        self._pystac_attempted = False
        self._chunking_attempted = False
        
        # Enhanced caching system
        self._all_items_cached = search_results.get('all_items_cached', False)
        self._all_items_cache = None
        self._fallback_metadata_cache = {}
        
        # Performance optimization: Extract and store the original limit
        self._original_limit = self._original_params.get('limit')
        self._respect_limit = True
        
        # 🚀 PERFORMANCE OPTIMIZATION: Pre-calculate if fallback is needed
        self._needs_fallback = self._calculate_fallback_need()
        
        # 🚀 PERFORMANCE OPTIMIZATION: Cache simple results immediately if sufficient
        if not self._needs_fallback:
            limited_items = self._apply_limit_if_needed(self._items)
            self._all_items_cache = STACItemCollection(limited_items, provider=self.provider)
            self._all_items_cached = True
    
    def _calculate_fallback_need(self) -> bool:
        """🚀 OPTIMIZATION: Pre-calculate if fallback is actually needed."""
        # No fallback needed if we have enough items for the requested limit
        if self._original_limit and len(self._items) >= self._original_limit:
            return False
        
        # No fallback needed if we have less than 100 items (not hitting API limit)
        if len(self._items) < 100:
            return False
        
        # Fallback needed if we hit the 100-item API limit and want more
        return len(self._items) == 100 and (not self._original_limit or self._original_limit > 100)
    
    def _apply_limit_if_needed(self, items_list: List) -> List:
        """🔧 Apply original limit to items if specified."""
        if self._respect_limit and self._original_limit and len(items_list) > self._original_limit:
            if self._verbose:
                print(f"🔧 Applying limit: {self._original_limit} items (was {len(items_list)})")
            return items_list[:self._original_limit]
        return items_list
    
    def get_all_items(self) -> STACItemCollection:
        """🚀 OPTIMIZED: Fast return for simple cases, fallback only when needed."""
        # 🚀 PERFORMANCE: Return cached result immediately if available
        if self._all_items_cache:
            return self._all_items_cache
        
        # 🚀 PERFORMANCE: Skip fallback logic entirely if not needed
        if not self._needs_fallback:
            limited_items = self._apply_limit_if_needed(self._items)
            self._all_items_cache = STACItemCollection(limited_items, provider=self.provider)
            return self._all_items_cache
        
        # Only attempt fallback if actually needed and not already attempted
        if not self._fallback_attempted and self._client:
            self._fallback_attempted = True
            
            if self._verbose:
                print(f"🔄 Attempting fallback strategies for {len(self._items)} items...")
            
            # Try pystac-client first
            pystac_result = self._try_pystac_fallback()
            if pystac_result:
                return pystac_result
            
            # Try chunking search as last resort
            chunking_result = self._try_chunking_fallback()
            if chunking_result:
                return chunking_result
            
            if self._verbose:
                print("⚠️ All fallback strategies failed, returning simple search results")
        
        # Return simple search results with limit applied
        limited_items = self._apply_limit_if_needed(self._items)
        self._all_items_cache = STACItemCollection(limited_items, provider=self.provider)
        return self._all_items_cache
    
    def _try_pystac_fallback(self) -> Optional[STACItemCollection]:
        """🔄 FALLBACK TIER 2: Try pystac-client pagination."""
        if self._pystac_attempted or not PYSTAC_AVAILABLE:
            return None
            
        self._pystac_attempted = True
        
        try:
            if self._verbose:
                print("🔄 Tier 2: Trying pystac-client fallback...")
            
            # Create pystac-client catalog for this provider
            pystac_catalog = self._client._create_pystac_catalog_fallback()
            if not pystac_catalog:
                return None
            
            # Create pystac-client search
            pystac_search = pystac_catalog.search(**self._original_params)
            
            # Suppress warnings and get all items
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning, module="pystac_client")
                warnings.filterwarnings("ignore", message=".*get_all_items.*deprecated.*")
                
                pystac_items = pystac_search.get_all_items()
                all_items_dicts = [item.to_dict() for item in pystac_items]
            
            # Apply limit to pystac results
            limited_items = self._apply_limit_if_needed(all_items_dicts)
            
            if self._verbose:
                print(f"  ✅ pystac-client retrieved {len(limited_items)} items")
            
            # Cache and return
            self._all_items_cache = STACItemCollection(limited_items, provider=self.provider)
            self._all_items_cached = True
            return self._all_items_cache
            
        except Exception as e:
            if self._verbose:
                print(f"  ❌ pystac-client fallback failed: {e}")
            return None
    
    def _try_chunking_fallback(self) -> Optional[STACItemCollection]:
        """🔄 FALLBACK TIER 3: Try own chunking search."""
        if self._chunking_attempted:
            return None
            
        self._chunking_attempted = True
        
        try:
            if self._verbose:
                print("🔄 Tier 3: Trying chunking fallback...")
            
            if hasattr(self._client, '_fallback_chunking_search'):
                chunked_items = self._client._fallback_chunking_search(
                    self._original_params,
                    self._search_url,
                    verbose=self._verbose
                )
                
                # Apply limit to chunking results
                limited_items = self._apply_limit_if_needed(chunked_items)
                
                if self._verbose:
                    print(f"  ✅ Chunking retrieved {len(limited_items)} items")
                
                # Cache and return
                self._all_items_cache = STACItemCollection(limited_items, provider=self.provider)
                self._all_items_cached = True
                return self._all_items_cache
                
        except Exception as e:
            if self._verbose:
                print(f"  ❌ Chunking fallback failed: {e}")
            return None
    
    def item_collection(self) -> STACItemCollection:
        """Alias for get_all_items()."""
        return self.get_all_items()
    
    def items(self):
        """🚀 OPTIMIZED: Return iterator over items with smart caching."""
        # Use cached items if available
        if self._all_items_cache:
            for item_data in self._all_items_cache._items:
                from .items import STACItem
                yield STACItem(item_data, provider=self.provider)
        else:
            # Use simple items with limit applied
            limited_items = self._apply_limit_if_needed(self._items)
            for item_data in limited_items:
                from .items import STACItem
                yield STACItem(item_data, provider=self.provider)
    
    def matched(self) -> Optional[int]:
        """Return total number of matched items."""
        if self._all_items_cache:
            return len(self._all_items_cache._items)
        return self._results.get('numberMatched', self._results.get('matched'))
    
    def total_items(self) -> Optional[int]:
        """Return total number of items."""
        if self._all_items_cache:
            return len(self._all_items_cache._items)
        return self._results.get('total_returned')
    
    def search_params(self) -> Optional[dict]:
        """Return search parameters used for the query."""
        return self._results.get('search_params', self._original_params)
    
    def all_keys(self) -> List[str]:
        """Return all keys from the search results."""
        return list(self._results.keys())
    
    def list_product_ids(self) -> List[str]:
        """🔧 FIXED: Return product IDs with simplified, reliable logic."""
        return [item.get("id") for item in self.items()]
    
    def get_fallback_status(self) -> Dict[str, Any]:
        """Get detailed fallback status information."""
        return {
            'needs_fallback': self._needs_fallback,
            'fallback_attempted': self._fallback_attempted,
            'pystac_attempted': self._pystac_attempted,
            'chunking_attempted': self._chunking_attempted,
            'all_items_cached': self._all_items_cached,
            'original_items_count': len(self._items),
            'cached_items_count': len(self._all_items_cache._items) if self._all_items_cache else None,
            'original_limit': self._original_limit,
            'respect_limit': self._respect_limit
        }
    
    def set_limit_enforcement(self, enforce: bool):
        """Control whether to enforce the original limit parameter."""
        self._respect_limit = enforce
        # Clear cache to force recalculation
        self._all_items_cache = None
        self._fallback_attempted = False
        self._needs_fallback = self._calculate_fallback_need()
    
    def __len__(self):
        """Return length with optimized caching."""
        if self._all_items_cache:
            return len(self._all_items_cache._items)
        return len(self._apply_limit_if_needed(self._items))
    
    def __repr__(self):
        """Enhanced representation with optimization info."""
        count = len(self)
        status = "cached" if self._all_items_cached else "simple"
        limit_info = f", limit={self._original_limit}" if self._original_limit else ""
        return f"STACSearch({count} items found, provider='{self.provider}', {status}{limit_info})"
