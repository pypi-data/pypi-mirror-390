"""Generic ArcGIS Feature Server client."""
import logging
import time
from typing import Dict, Generator, Optional, List, Union
import requests

from .auth import AuthStrategy, NoAuth, UsernamePasswordAuth, TokenAuth

log = logging.getLogger(__name__)


class ArcGISClient:
    """
    Generic client for ArcGIS Feature Servers.

    Works with any ArcGIS REST API endpoint. Not tied to any specific server or layers.

    Examples:
        >>> # Public layer (no auth)
        >>> client = ArcGISClient()
        >>>
        >>> # Authenticated
        >>> from cityofboston.arcgis.auth import UsernamePasswordAuth
        >>> auth = UsernamePasswordAuth(
        ...     portal_url="https://portal.example.com",
        ...     username="user",
        ...     password="pass"
        ... )
        >>> client = ArcGISClient(auth=auth)
    """

    def __init__(self, auth: Optional[AuthStrategy] = None):
        """
        Initialize ArcGIS client.

        Args:
            auth: Authentication strategy. If None, uses NoAuth for public layers.
        """
        self.auth = auth or NoAuth()
        self._layer_metadata_cache: Dict[str, Dict] = {}

    def get_feature_count(self, layer_url: str, where: str = "1=1") -> int:
        """
        Get the total number of features in a layer.

        Args:
            layer_url: Full URL to the feature layer
            where: SQL WHERE clause to filter features

        Returns:
            Number of features matching the where clause
        """
        url = f"{layer_url.rstrip('/')}/query"

        params = {
            'where': where,
            'returnCountOnly': 'true',
            'f': 'json'
        }

        # Add token if authenticated
        token = self.auth.get_token()
        if token:
            params['token'] = token

        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()

        if 'error' in result:
            raise Exception(f"ArcGIS API error: {result['error']}")

        return result.get('count', 0)

    def query_features(
        self,
        layer_url: str,
        where: str = "1=1",
        out_fields: str = "*",
        page_size: int = 2000,
        offset: int = 0,
        order_by_fields: Optional[str] = None,
        return_geometry: bool = True,
        max_features: Optional[int] = None
    ) -> Generator[Dict, None, None]:
        """
        Query features from a layer with pagination.

        Args:
            layer_url: Full URL to the feature layer
            where: SQL WHERE clause
            out_fields: Fields to return (default "*" for all)
            page_size: Number of records per page
            offset: Starting offset for pagination
            order_by_fields: Field(s) to order by (e.g., "OBJECTID" or "OBJECTID ASC")
            return_geometry: Whether to include geometry
            max_features: Maximum number of features to return (None = all)

        Yields:
            Feature dictionaries with attributes and geometry merged together
        """
        url = f"{layer_url.rstrip('/')}/query"

        # Get total features if we need to track progress
        total_features = self.get_feature_count(layer_url, where)

        if offset >= total_features:
            log.info("Offset exceeds total features. Exiting")
            return

        log.info(
            f"Starting query from {layer_url} "
            f"(offset={offset}, total={total_features}, order_by={order_by_fields})"
        )

        features_yielded = 0
        page_num = 0
        start_time = time.time()

        while True:
            page_num += 1

            params = {
                'where': where,
                'outFields': out_fields,
                'resultOffset': offset,
                'resultRecordCount': page_size,
                'f': 'json',
                'returnGeometry': 'true' if return_geometry else 'false'
            }

            if order_by_fields:
                params['orderByFields'] = order_by_fields

            # Add token if authenticated
            token = self.auth.get_token()
            if token:
                params['token'] = token

            try:
                page_start = time.time()
                response = requests.get(url, params=params)
                response.raise_for_status()
                result = response.json()
                page_duration = time.time() - page_start

                if 'error' in result:
                    log.error(f"API error: {result['error']}")
                    break

                log.debug(f"Query page {page_num} completed in {page_duration:.2f}s")

            except Exception as e:
                log.exception(f"Query failed on page {page_num} (offset={offset}): {e}")
                break

            features = result.get('features', [])

            if not features:
                log.info("No more features returned")
                break

            result_count = len(features)
            features_yielded += result_count

            log.info(
                f"Page {page_num}: {result_count} features "
                f"(total yielded: {features_yielded}/{total_features}, "
                f"{(features_yielded / total_features * 100):.1f}%)"
            )

            for feature in features:
                # Merge attributes and geometry into single dict
                final_obj = feature.get('attributes', {})
                if 'geometry' in feature and feature['geometry']:
                    final_obj.update(feature['geometry'])
                yield final_obj

                # Stop if we've hit max_features limit
                if max_features and features_yielded >= max_features:
                    log.info(f"Reached max_features limit ({max_features})")
                    return

            # Check if we're done
            if features_yielded >= total_features:
                log.info("Retrieved all features")
                break

            if result_count < page_size:
                log.info("Last page reached (partial page)")
                break

            offset = min(offset + page_size, total_features)

        duration = time.time() - start_time
        log.info(f"Query complete: {features_yielded} features in {duration:.2f}s")

    def get_layer_metadata(self, layer_url: str, use_cache: bool = True) -> Dict:
        """
        Get metadata for a feature layer.

        Args:
            layer_url: Full URL to the feature layer
            use_cache: Whether to use cached metadata

        Returns:
            Layer metadata dictionary including fields, geometry type, etc.
        """
        if use_cache and layer_url in self._layer_metadata_cache:
            return self._layer_metadata_cache[layer_url]

        url = layer_url.rstrip('/')
        params = {'f': 'json'}

        token = self.auth.get_token()
        if token:
            params['token'] = token

        response = requests.get(url, params=params)
        response.raise_for_status()
        metadata = response.json()

        if 'error' in metadata:
            raise Exception(f"ArcGIS API error: {metadata['error']}")

        self._layer_metadata_cache[layer_url] = metadata
        return metadata

    def get_field_names(self, layer_url: str) -> List[str]:
        """
        Get all field names for a layer.

        Args:
            layer_url: Full URL to the feature layer

        Returns:
            List of field names
        """
        metadata = self.get_layer_metadata(layer_url)
        return [field['name'] for field in metadata.get('fields', [])]

    def update_features(
        self,
        layer_url: str,
        updates: List[Dict],
        rollback_on_failure: bool = True
    ) -> Dict:
        """
        Update features in a feature layer.

        Args:
            layer_url: Full URL to the feature layer
            updates: List of features to update. Each should have 'attributes' with OBJECTID
            rollback_on_failure: Whether to rollback all changes if any fail

        Returns:
            Results dictionary from the applyEdits operation

        Example:
            >>> updates = [
            ...     {"attributes": {"OBJECTID": 123, "ZIP_CODE": "02127"}},
            ...     {"attributes": {"OBJECTID": 456, "ZIP_CODE": "02115"}}
            ... ]
            >>> result = client.update_features(layer_url, updates)
        """
        url = f"{layer_url.rstrip('/')}/applyEdits"

        params = {
            'updates': str(updates).replace("'", '"'),  # Convert to JSON string
            'f': 'json',
            'rollbackOnFailure': 'true' if rollback_on_failure else 'false'
        }

        token = self.auth.get_token()
        if token:
            params['token'] = token

        try:
            response = requests.post(url, data=params)
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                log.error(f"Error updating features: {result['error']}")
                raise Exception(f"ArcGIS API error: {result['error']}")

            update_results = result.get('updateResults', [])
            success_count = sum(1 for r in update_results if r.get('success'))

            log.info(f"Updated {success_count}/{len(updates)} features")

            # Log failures
            failures = [r for r in update_results if not r.get('success')]
            if failures:
                log.warning(f"{len(failures)} updates failed")
                for failure in failures[:5]:
                    error_desc = failure.get('error', {}).get('description', 'Unknown')
                    log.warning(f"  OBJECTID {failure.get('objectId')}: {error_desc}")

            return result

        except Exception as e:
            log.error(f"Error in update_features: {e}")
            raise

    def export_to_csv(
        self,
        layer_url: str,
        output_path: str,
        where: str = "1=1",
        out_fields: str = "*",
        page_size: int = 2000
    ):
        """
        Export layer data to CSV.

        Args:
            layer_url: Full URL to the feature layer
            output_path: Path to output CSV file
            where: SQL WHERE clause to filter features
            out_fields: Fields to export
            page_size: Number of records per page
        """
        import csv

        log.info(f"Exporting data to {output_path}")

        # Get field names
        if out_fields == "*":
            field_names = self.get_field_names(layer_url)
        else:
            field_names = [f.strip() for f in out_fields.split(',')]

        # Write to CSV
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_names, extrasaction='ignore')
            writer.writeheader()

            for feature in self.query_features(
                layer_url,
                where=where,
                out_fields=out_fields,
                page_size=page_size,
                return_geometry=True
            ):
                writer.writerow(feature)

        log.info(f"Export complete: {output_path}")
