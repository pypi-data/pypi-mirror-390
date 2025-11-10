"""
Unified STAC Client for Open Geodata API
========================================

A flexible client for connecting to any STAC-compliant API endpoint
with optional authentication.
"""

from .client import UnifiedSTACClient, create_unified_client

__version__ = "0.1.0"
__all__ = ["UnifiedSTACClient", "create_unified_client"]
