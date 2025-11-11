"""Generic ArcGIS utilities for working with any Feature Server."""
from .client import ArcGISClient
from .auth import AuthStrategy, NoAuth, TokenAuth, UsernamePasswordAuth

__all__ = [
    'ArcGISClient',
    'AuthStrategy',
    'NoAuth',
    'TokenAuth',
    'UsernamePasswordAuth',
]
