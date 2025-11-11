"""Convenience client for City of Boston SAM data."""
import logging
from typing import Dict, Generator, Optional, List

from ..arcgis.client import ArcGISClient
from ..arcgis.auth import AuthStrategy, UsernamePasswordAuth
from .layers import SAMLayer, SAMEnvironment, get_layer_url, get_portal_url, get_geometry_fields

log = logging.getLogger(__name__)


class SAMClient:
    """
    Convenience wrapper for working with City of Boston SAM (Street Address Management) data.

    Provides easy access to SAM feature layers with pre-configured URLs and authentication.

    Examples:
        >>> # Using environment variables for credentials
        >>> client = SAMClient(environment=SAMEnvironment.TEST)
        >>>
        >>> # Passing credentials directly
        >>> client = SAMClient(
        ...     environment=SAMEnvironment.PROD,
        ...     username="myuser",
        ...     password="mypass"
        ... )
        >>>
        >>> # Query addresses
        >>> for address in client.query_layer(SAMLayer.ADDRESSES, where="ZIP_CODE='02127'"):
        ...     print(address)
    """

    def __init__(
        self,
        environment: SAMEnvironment = SAMEnvironment.TEST,
        auth: Optional[AuthStrategy] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize SAM client.

        Args:
            environment: Test or production environment
            auth: Authentication strategy (if provided, username/password are ignored)
            username: ArcGIS username (convenience for creating UsernamePasswordAuth)
            password: ArcGIS password (convenience for creating UsernamePasswordAuth)

        Environment variables (used if auth and username/password not provided):
            - For TEST: TEST_ARCGIS_USERNAME, TEST_ARCGIS_PASSWORD
            - For PROD: PROD_ARCGIS_USERNAME, PROD_ARCGIS_PASSWORD

        Examples:
            >>> # Use custom auth strategy
            >>> from cityofboston.arcgis.auth import TokenAuth
            >>> auth = TokenAuth("my-token")
            >>> client = SAMClient(auth=auth)
            >>>
            >>> # Convenience: pass username/password
            >>> client = SAMClient(username="user", password="pass")
            >>>
            >>> # Convenience: use environment variables
            >>> client = SAMClient()  # Reads from TEST_ARCGIS_USERNAME/PASSWORD
        """
        self.environment = environment
        portal_url = get_portal_url(environment)

        # If auth strategy provided, use it
        if auth is not None:
            self.client = ArcGISClient(auth=auth)
        # Otherwise, create UsernamePasswordAuth (either from params or env vars)
        else:
            env_prefix = "TEST" if environment == SAMEnvironment.TEST else "PROD"
            env_username_key = f"{env_prefix}_ARCGIS_USERNAME"
            env_password_key = f"{env_prefix}_ARCGIS_PASSWORD"

            auth = UsernamePasswordAuth(
                portal_url=portal_url,
                username=username,
                password=password,
                env_username_key=env_username_key,
                env_password_key=env_password_key
            )
            self.client = ArcGISClient(auth=auth)

        log.info(f"SAM client initialized for {environment.value} environment")

    def get_layer_url(self, layer: SAMLayer) -> str:
        """Get the full URL for a SAM layer."""
        return get_layer_url(layer, self.environment)

    def get_feature_count(self, layer: SAMLayer, where: str = "1=1") -> int:
        """
        Get the number of features in a SAM layer.

        Args:
            layer: SAM layer to query
            where: SQL WHERE clause to filter features

        Returns:
            Number of features
        """
        return self.client.get_feature_count(self.get_layer_url(layer), where)

    def query_layer(
        self,
        layer: SAMLayer,
        where: str = "1=1",
        out_fields: str = "*",
        page_size: int = 2000,
        offset: int = 0,
        order_by_fields: Optional[str] = None,
        return_geometry: bool = True,
        max_features: Optional[int] = None
    ) -> Generator[Dict, None, None]:
        """
        Query features from a SAM layer.

        Args:
            layer: SAM layer to query
            where: SQL WHERE clause
            out_fields: Fields to return (default "*" for all)
            page_size: Number of records per page
            offset: Starting offset for pagination
            order_by_fields: Field(s) to order by
            return_geometry: Whether to include geometry
            max_features: Maximum number of features to return

        Yields:
            Feature dictionaries with attributes and geometry
        """
        return self.client.query_features(
            layer_url=self.get_layer_url(layer),
            where=where,
            out_fields=out_fields,
            page_size=page_size,
            offset=offset,
            order_by_fields=order_by_fields,
            return_geometry=return_geometry,
            max_features=max_features
        )

    def get_field_names(self, layer: SAMLayer) -> List[str]:
        """
        Get all field names for a SAM layer.

        Args:
            layer: SAM layer

        Returns:
            List of field names (including geometry fields)
        """
        attribute_fields = self.client.get_field_names(self.get_layer_url(layer))
        geometry_fields = get_geometry_fields(layer)
        return attribute_fields + geometry_fields

    def export_to_csv(
        self,
        layer: SAMLayer,
        output_path: str,
        where: str = "1=1",
        out_fields: str = "*",
        page_size: int = 2000
    ):
        """
        Export SAM layer data to CSV.

        Args:
            layer: SAM layer to export
            output_path: Path to output CSV file
            where: SQL WHERE clause to filter features
            out_fields: Fields to export
            page_size: Number of records per page
        """
        self.client.export_to_csv(
            layer_url=self.get_layer_url(layer),
            output_path=output_path,
            where=where,
            out_fields=out_fields,
            page_size=page_size
        )

    def update_features(
        self,
        layer: SAMLayer,
        updates: List[Dict],
        rollback_on_failure: bool = True
    ) -> Dict:
        """
        Update features in a SAM layer.

        Args:
            layer: SAM layer to update
            updates: List of features to update (must include OBJECTID in attributes)
            rollback_on_failure: Whether to rollback all changes if any fail

        Returns:
            Results dictionary from the update operation

        Example:
            >>> updates = [
            ...     {"attributes": {"OBJECTID": 123, "ZIP_CODE": "02127"}},
            ...     {"attributes": {"OBJECTID": 456, "ZIP_CODE": "02115"}}
            ... ]
            >>> client.update_features(SAMLayer.ADDRESSES, updates)
        """
        return self.client.update_features(
            layer_url=self.get_layer_url(layer),
            updates=updates,
            rollback_on_failure=rollback_on_failure
        )

    def get_street_name_by_segment_id(self, segment_id: int) -> Optional[str]:
        """
        Look up street name by segment ID.

        Args:
            segment_id: The SEGMENT_ID to look up

        Returns:
            Street name string, or None if not found
        """
        if not segment_id:
            return None

        features = list(self.query_layer(
            layer=SAMLayer.STREET_SEGMENTS,
            where=f'SEGMENT_ID = {segment_id}',
            out_fields='FULL_STREET_NAME',
            return_geometry=False,
            max_features=1
        ))

        if features:
            return features[0].get('FULL_STREET_NAME')

        return None
