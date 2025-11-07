"""Adobe Customer Journey Analytics API client."""

from typing import Any, Optional

import httpx

from adobe_cja_mcp.auth.oauth import AdobeOAuthClient
from adobe_cja_mcp.utils.config import Settings


class CJAClientError(Exception):
    """Base exception for CJA client errors."""

    pass


class CJAAuthenticationError(CJAClientError):
    """Authentication failed."""

    pass


class CJAAPIError(CJAClientError):
    """API request failed."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class CJAClient:
    """Client for interacting with Adobe Customer Journey Analytics API.

    This client handles authenticated HTTP requests to the CJA API,
    including automatic token management and error handling.
    """

    def __init__(self, settings: Settings, oauth_client: AdobeOAuthClient) -> None:
        """Initialize CJA API client.

        Args:
            settings: Application settings.
            oauth_client: OAuth client for authentication.
        """
        self.settings = settings
        self.oauth_client = oauth_client
        self._http_client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "CJAClient":
        """Async context manager entry."""
        self._http_client = httpx.AsyncClient(
            timeout=self.settings.request_timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._http_client:
            await self._http_client.aclose()

    def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client, creating if necessary."""
        if not self._http_client:
            self._http_client = httpx.AsyncClient(
                timeout=self.settings.request_timeout,
                follow_redirects=True,
            )
        return self._http_client

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        retries: int = 0,
    ) -> dict[str, Any]:
        """Make authenticated request to CJA API.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            params: URL query parameters.
            json_data: JSON request body.
            retries: Current retry count.

        Returns:
            dict: JSON response from API.

        Raises:
            CJAAuthenticationError: If authentication fails.
            CJAAPIError: If API request fails.
        """
        url = self.settings.get_api_url(path)
        headers = await self.oauth_client.get_auth_headers()
        client = self._get_client()

        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
            )

            # Handle 401 - try to refresh token once
            if response.status_code == 401 and retries < 1:
                self.oauth_client.invalidate_token()
                return await self._request(method, path, params, json_data, retries + 1)

            response.raise_for_status()

            # Return JSON response
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise CJAAuthenticationError(f"Authentication failed: {e}") from e
            else:
                error_data = None
                try:
                    error_data = e.response.json()
                except Exception:
                    error_data = e.response.text

                # Include request details in error message for debugging
                # Don't include full request body - it may contain sensitive filter criteria
                error_msg = f"API request failed: {method} {url} - Status {e.response.status_code}"
                if error_data:
                    error_msg += f"\nResponse: {error_data}"
                if json_data:
                    # Only include request structure for debugging (not full values)
                    error_msg += f"\nRequest keys: {list(json_data.keys())}"

                raise CJAAPIError(
                    error_msg,
                    status_code=e.response.status_code,
                    response_data=error_data,
                ) from e
        except httpx.RequestError as e:
            raise CJAAPIError(f"Request error: {e}") from e

    async def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make GET request to CJA API.

        Args:
            path: API endpoint path.
            params: URL query parameters.

        Returns:
            dict: JSON response.
        """
        return await self._request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json_data: dict[str, Any],
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make POST request to CJA API.

        Args:
            path: API endpoint path.
            json_data: JSON request body.
            params: URL query parameters.

        Returns:
            dict: JSON response.
        """
        return await self._request("POST", path, params=params, json_data=json_data)

    # Convenience methods for common CJA API operations

    async def list_dimensions(self, dataview_id: Optional[str] = None) -> dict[str, Any]:
        """List all dimensions for a data view.

        Args:
            dataview_id: Data view ID (defaults to configured ID).

        Returns:
            dict: Dimensions list response.
        """
        dv_id = dataview_id or self.settings.adobe_data_view_id
        return await self.get(f"/data/dataviews/{dv_id}/dimensions")

    async def list_metrics(self, dataview_id: Optional[str] = None) -> dict[str, Any]:
        """List all metrics for a data view.

        Args:
            dataview_id: Data view ID (defaults to configured ID).

        Returns:
            dict: Metrics list response.
        """
        dv_id = dataview_id or self.settings.adobe_data_view_id
        return await self.get(f"/data/dataviews/{dv_id}/metrics")

    async def run_report(
        self,
        request_body: dict[str, Any],
        dataview_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a reporting request.

        Args:
            request_body: Report request definition.
            dataview_id: Data view ID (defaults to configured ID).

        Returns:
            dict: Report results.
        """
        dv_id = dataview_id or self.settings.adobe_data_view_id
        # Add dataId (data view ID) to request body - this is what CJA API actually expects
        request_body["dataId"] = dv_id
        return await self.post("/reports", json_data=request_body)

    async def get_dataview(self, dataview_id: Optional[str] = None) -> dict[str, Any]:
        """Get data view details.

        Args:
            dataview_id: Data view ID (defaults to configured ID).

        Returns:
            dict: Data view configuration.
        """
        dv_id = dataview_id or self.settings.adobe_data_view_id
        return await self.get(f"/data/dataviews/{dv_id}")

    async def list_segments(
        self,
        dataview_id: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """List all segments.

        Args:
            dataview_id: Optional data view ID to filter segments (rsids param).
            params: Optional additional query parameters.

        Returns:
            dict: Segments list response.
        """
        query_params = params or {}
        if dataview_id:
            query_params["rsids"] = dataview_id
        return await self.get("/segments", params=query_params)

    async def get_segment(
        self,
        segment_id: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Get a specific segment by ID.

        Args:
            segment_id: Segment ID to retrieve.
            params: Optional query parameters (e.g., expansion).

        Returns:
            dict: Segment details.
        """
        return await self.get(f"/segments/{segment_id}", params=params)

    async def create_segment(
        self,
        segment_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new segment.

        Args:
            segment_data: Segment definition including name, description, dataId, and definition.

        Returns:
            dict: Created segment with assigned ID.
        """
        return await self.post("/segments", json_data=segment_data)

    async def update_segment(
        self,
        segment_id: str,
        segment_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing segment.

        Args:
            segment_id: Segment ID to update.
            segment_data: Updated segment data (partial update supported).

        Returns:
            dict: Updated segment.
        """
        return await self._request("PUT", f"/segments/{segment_id}", json_data=segment_data)

    async def validate_segment(
        self,
        definition: dict[str, Any],
        dataview_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Validate a segment definition.

        Args:
            definition: Segment definition to validate.
            dataview_id: Data view ID to validate against (defaults to configured ID).
            name: Optional segment name for validation.
            description: Optional segment description for validation.

        Returns:
            dict: Validation result.
        """
        dv_id = dataview_id or self.settings.adobe_data_view_id
        # CJA API requires dataId in the request body, not as query parameter
        # See: https://developer.adobe.com/cja-apis/docs/endpoints/segments/validate/
        request_body: dict[str, Any] = {
            "dataId": dv_id,
            "definition": definition,
        }

        # Add optional fields
        if name:
            request_body["name"] = name
        if description:
            request_body["description"] = description

        return await self.post("/segments/validate", json_data=request_body)

    async def delete_segment(
        self,
        segment_id: str,
    ) -> dict[str, Any]:
        """Delete a segment.

        Args:
            segment_id: Segment ID to delete.

        Returns:
            dict: Deletion confirmation.
        """
        return await self._request("DELETE", f"/segments/{segment_id}")

    # Calculated Metrics API methods (Phase 3)

    async def list_calculated_metrics(
        self,
        dataview_id: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """List all calculated metrics.

        Args:
            dataview_id: Optional data view ID to filter metrics.
            params: Optional additional query parameters.

        Returns:
            dict: Calculated metrics list response.
        """
        query_params = params or {}
        if dataview_id:
            query_params["dataId"] = dataview_id
        return await self.get("/calculatedmetrics", params=query_params)

    async def get_calculated_metric(
        self,
        metric_id: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Get a specific calculated metric by ID.

        Args:
            metric_id: Calculated metric ID to retrieve.
            params: Optional query parameters (e.g., expansion).

        Returns:
            dict: Calculated metric details.
        """
        return await self.get(f"/calculatedmetrics/{metric_id}", params=params)

    async def create_calculated_metric(
        self,
        metric_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new calculated metric.

        Args:
            metric_data: Metric definition including name, description, dataId, type, and definition.

        Returns:
            dict: Created calculated metric with assigned ID.
        """
        return await self.post("/calculatedmetrics", json_data=metric_data)

    async def update_calculated_metric(
        self,
        metric_id: str,
        metric_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing calculated metric.

        Args:
            metric_id: Calculated metric ID to update.
            metric_data: Updated metric data (partial update supported).

        Returns:
            dict: Updated calculated metric.
        """
        return await self._request("PUT", f"/calculatedmetrics/{metric_id}", json_data=metric_data)

    async def validate_calculated_metric(
        self,
        definition: dict[str, Any],
        name: str,
        metric_type: str = "decimal",
        dataview_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Validate a calculated metric definition.

        Args:
            definition: Calculated metric definition to validate.
            name: Metric name for validation.
            metric_type: Metric type (decimal, percent, currency, time).
            dataview_id: Data view ID to validate against (defaults to configured ID).
            description: Optional metric description for validation.

        Returns:
            dict: Validation result.
        """
        dv_id = dataview_id or self.settings.adobe_data_view_id
        # CJA API requires dataId in the request body
        request_body: dict[str, Any] = {
            "dataId": dv_id,
            "name": name,
            "type": metric_type,
            "definition": definition,
        }

        # Add optional fields
        if description:
            request_body["description"] = description

        return await self.post("/calculatedmetrics/validate", json_data=request_body)

    async def delete_calculated_metric(
        self,
        metric_id: str,
    ) -> dict[str, Any]:
        """Delete a calculated metric.

        Args:
            metric_id: Calculated metric ID to delete.

        Returns:
            dict: Deletion confirmation.
        """
        return await self._request("DELETE", f"/calculatedmetrics/{metric_id}")

    async def close(self) -> None:
        """Close HTTP client connection."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
