"""
Configuration management for open-geodata-api
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union


# Global configuration storage
_GLOBAL_CONFIG = {
    'default_provider': 'planetary_computer',
    'auto_sign_urls': True,
    'max_download_workers': 4,
    'default_timeout': 120,
    'batch_size': 10,
    'cache_size_mb': 500,
    'progress_bar': True,
    'verbose_errors': False,
    'debug_mode': False,
    'max_retries': 3,
    'chunk_size': 16384,
    'verify_downloads': False
}


def set_global_config(**config_params) -> Dict[str, Any]:
    """
    Set global configuration parameters for the library.
    
    Args:
        **config_params: Configuration parameters to set
        
    Returns:
        Updated configuration dictionary
    """
    global _GLOBAL_CONFIG
    
    _GLOBAL_CONFIG.update(config_params)
    return _GLOBAL_CONFIG.copy()


def get_global_config(key: Optional[str] = None) -> Union[Any, Dict[str, Any]]:
    """
    Get global configuration parameters.
    
    Args:
        key: Specific configuration key (None for all)
        
    Returns:
        Configuration value or full configuration
    """
    if key is None:
        return _GLOBAL_CONFIG.copy()
    return _GLOBAL_CONFIG.get(key)


def optimize_for_large_datasets(dataset_size_gb: float, available_memory_gb: float) -> Dict[str, Any]:
    """
    Optimize library settings for large dataset processing.
    
    Args:
        dataset_size_gb: Expected dataset size in GB
        available_memory_gb: Available system memory in GB
        
    Returns:
        Optimized configuration recommendations
    """
    
    # Calculate optimal settings
    memory_per_worker = available_memory_gb / 8  # Conservative estimate
    max_workers = min(8, max(1, int(available_memory_gb / 2)))
    
    # Adjust batch size based on dataset size
    if dataset_size_gb > 100:
        batch_size = 5
        strategy = "conservative"
    elif dataset_size_gb > 50:
        batch_size = 10
        strategy = "balanced"
    else:
        batch_size = 20
        strategy = "aggressive"
    
    # Calculate cache size (10% of available memory, max 2GB)
    cache_size_mb = min(2000, int(available_memory_gb * 100))
    
    optimization = {
        'batch_size': batch_size,
        'max_workers': max_workers,
        'memory_per_worker_mb': int(memory_per_worker * 1024),
        'strategy': strategy,
        'config': {
            'max_download_workers': max_workers,
            'batch_size': batch_size,
            'cache_size_mb': cache_size_mb,
            'memory_limit_gb': available_memory_gb * 0.8,
            'chunk_size': 32768 if strategy == "aggressive" else 16384
        }
    }
    
    return optimization
