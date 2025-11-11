# cityofboston

City of Boston Python utilities for working with ArcGIS Feature Servers and Boston-specific data systems.

## Features

### Generic ArcGIS Client (`cityofboston.arcgis`)
- Work with **any** ArcGIS Feature Server
- Flexible authentication (username/password, token, or anonymous)
- Pagination support for large datasets
- Export to CSV
- Update features

### SAM Client (`cityofboston.sam`)
- Convenience wrapper for Boston's Street Address Management (SAM) system
- Pre-configured layer definitions for TEST and PROD environments
- Easy access to addresses, buildings, street segments, and more

## Installation

```bash
pip install cityofboston
```

### Optional dependencies

For geospatial export formats (GeoJSON, Shapefile, GeoPackage):
```bash
pip install cityofboston[geo]
```

For development:
```bash
pip install cityofboston[dev]
```

## Usage

### Generic ArcGIS Client

Work with any ArcGIS Feature Server:

```python
from cityofboston.arcgis import ArcGISClient, UsernamePasswordAuth

# Authenticated access
auth = UsernamePasswordAuth(
    portal_url="https://portal.example.com",
    username="myuser",
    password="mypass"
)
client = ArcGISClient(auth=auth)

# Query features
layer_url = "https://services.arcgis.com/ORG/arcgis/rest/services/MyService/FeatureServer/0"
for feature in client.query_features(layer_url, where="STATE='MA'"):
    print(feature)

# Get feature count
count = client.get_feature_count(layer_url, where="STATE='MA'")
print(f"Found {count} features")

# Export to CSV
client.export_to_csv(layer_url, "output.csv", where="STATE='MA'")
```

### SAM Client

Easy access to Boston's Street Address Management data:

```python
from cityofboston.sam import SAMClient, SAMLayer, SAMEnvironment

# Connect to TEST environment (reads credentials from env vars)
client = SAMClient(environment=SAMEnvironment.TEST)

# Or pass credentials directly
client = SAMClient(
    environment=SAMEnvironment.PROD,
    username="myuser",
    password="mypass"
)

# Query addresses in a specific ZIP code
for address in client.query_layer(
    SAMLayer.ADDRESSES,
    where="ZIP_CODE='02127'"
):
    print(address)

# Get feature count
count = client.get_feature_count(SAMLayer.ADDRESSES)
print(f"Total addresses: {count}")

# Export to CSV
client.export_to_csv(
    SAMLayer.ADDRESSES,
    "addresses.csv",
    where="ZIP_CODE='02127'"
)

# Update features
updates = [
    {"attributes": {"OBJECTID": 123, "ZIP_CODE": "02127"}},
    {"attributes": {"OBJECTID": 456, "ZIP_CODE": "02115"}}
]
result = client.update_features(SAMLayer.ADDRESSES, updates)

# Lookup street name by segment ID
street_name = client.get_street_name_by_segment_id(12345)
```

### Available SAM Layers

- `SAMLayer.ADDRESSES` - Address points
- `SAMLayer.BUILDINGS` - Building polygons
- `SAMLayer.STREET_SEGMENTS` - Street centerlines
- `SAMLayer.MASTER_STREET_NAMES` - Master street name table
- `SAMLayer.STREET_ALIASES` - Street name aliases
- `SAMLayer.BOSTON_ZIP_CODES` - ZIP code boundaries

## Authentication

### Environment Variables

The SAM client reads credentials from environment variables by default:

**For TEST environment:**
- `TEST_ARCGIS_USERNAME`
- `TEST_ARCGIS_PASSWORD`

**For PROD environment:**
- `PROD_ARCGIS_USERNAME`
- `PROD_ARCGIS_PASSWORD`

Create a `.env` file:
```bash
TEST_ARCGIS_USERNAME=myuser
TEST_ARCGIS_PASSWORD=mypass
```

### Direct Credentials

You can also pass credentials directly:

```python
from cityofboston.sam import SAMClient, SAMEnvironment

client = SAMClient(
    environment=SAMEnvironment.PROD,
    username="myuser",
    password="mypass"
)
```

### Public/Anonymous Access

For public layers that don't require authentication:

```python
from cityofboston.arcgis import ArcGISClient

client = ArcGISClient()  # No auth needed
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and building.

```bash
# Clone the repository
git clone https://github.com/CityOfBoston/cityofboston-python.git
cd cityofboston-python

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"

# Run tests
uv run pytest
```

## Publishing to PyPI

This package is published to PyPI under the `cityofboston` organization. Publishing is automated via GitHub Actions when a new release is created.

### Manual Publishing

If you need to publish manually:

```bash
# Build the package using uv
uv build

# Upload to PyPI (requires PyPI credentials)
uv publish
```

## Contributing

Issues and pull requests welcome at https://github.com/CityOfBoston/cityofboston-python
