"""City of Boston SAM (Street Address Management) layer definitions."""
from enum import Enum
from typing import Dict, List


class SAMLayer(Enum):
    """SAM feature layer identifiers."""
    ADDRESSES = 'ADDRESSES'
    BUILDINGS = 'BUILDINGS'
    STREET_SEGMENTS = 'STREET_SEGMENTS'
    MASTER_STREET_NAMES = 'MASTER_STREET_NAMES'
    STREET_ALIASES = 'STREET_ALIASES'
    BOSTON_ZIP_CODES = 'BOSTON_ZIP_CODES'


class SAMEnvironment(Enum):
    """SAM environment (test vs production)."""
    TEST = 'TEST'
    PROD = 'PROD'


# SAM Feature Server configurations
SAM_CONFIGS = {
    SAMEnvironment.TEST: {
        "portal_url": "https://testgisportal.boston.gov/portal",
        "feature_server_base": "https://testgisportal.boston.gov/arcgis/rest/services/SAM/SAM_editing/FeatureServer",
        "layers": {
            SAMLayer.ADDRESSES: {
                'layer_index': 0,
                'geometry_type': 'point',
                'geometry_fields': ['x', 'y', 'spatialReference']
            },
            SAMLayer.BUILDINGS: {
                'layer_index': 1,
                'geometry_type': 'polygon',
                'geometry_fields': ['rings', 'spatialReference']
            },
            SAMLayer.STREET_SEGMENTS: {
                'layer_index': 2,
                'geometry_type': 'polyline',
                'geometry_fields': ['paths', 'spatialReference']
            },
            SAMLayer.MASTER_STREET_NAMES: {
                'layer_index': 11,
                'geometry_type': 'none',
                'geometry_fields': []
            },
            SAMLayer.STREET_ALIASES: {
                'layer_index': 12,
                'geometry_type': 'none',
                'geometry_fields': []
            },
            SAMLayer.BOSTON_ZIP_CODES: {
                'layer_index': 10,
                'geometry_type': 'polygon',
                'geometry_fields': ['rings', 'spatialReference']
            }
        }
    },
    SAMEnvironment.PROD: {
        "portal_url": "https://gisportal.boston.gov/portal",
        "feature_server_base": "https://gisportal.boston.gov/arcgis/rest/services/SAM/SAM_editing/FeatureServer",
        "layers": {
            SAMLayer.ADDRESSES: {
                'layer_index': 0,
                'geometry_type': 'point',
                'geometry_fields': ['x', 'y', 'spatialReference']
            },
            SAMLayer.BUILDINGS: {
                'layer_index': 1,
                'geometry_type': 'polygon',
                'geometry_fields': ['rings', 'spatialReference']
            },
            SAMLayer.STREET_SEGMENTS: {
                'layer_index': 2,
                'geometry_type': 'polyline',
                'geometry_fields': ['paths', 'spatialReference']
            },
            SAMLayer.MASTER_STREET_NAMES: {
                'layer_index': 11,
                'geometry_type': 'none',
                'geometry_fields': []
            },
            SAMLayer.STREET_ALIASES: {
                'layer_index': 12,
                'geometry_type': 'none',
                'geometry_fields': []
            },
            SAMLayer.BOSTON_ZIP_CODES: {
                'layer_index': 10,
                'geometry_type': 'polygon',
                'geometry_fields': ['rings', 'spatialReference']
            }
        }
    }
}


def get_layer_url(layer: SAMLayer, environment: SAMEnvironment = SAMEnvironment.TEST) -> str:
    """
    Get the feature server URL for a SAM layer.

    Args:
        layer: SAM layer identifier
        environment: Test or production environment

    Returns:
        Full URL to the feature layer
    """
    config = SAM_CONFIGS[environment]
    layer_index = config['layers'][layer]['layer_index']
    return f"{config['feature_server_base']}/{layer_index}"


def get_geometry_fields(layer: SAMLayer) -> List[str]:
    """
    Get geometry field names for a SAM layer.

    Args:
        layer: SAM layer identifier

    Returns:
        List of geometry field names
    """
    # Geometry fields are the same across environments
    return SAM_CONFIGS[SAMEnvironment.TEST]['layers'][layer]['geometry_fields']


def get_portal_url(environment: SAMEnvironment = SAMEnvironment.TEST) -> str:
    """
    Get the portal URL for a SAM environment.

    Args:
        environment: Test or production environment

    Returns:
        Portal URL
    """
    return SAM_CONFIGS[environment]['portal_url']
