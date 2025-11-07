"""OAuth Server-to-Server authentication for Adobe IMS."""

import time
from typing import Optional

import httpx

from adobe_cja_mcp.utils.config import Settings


class AdobeOAuthClient:
    """Handles OAuth 2.0 Server-to-Server authentication with Adobe IMS.

    This client manages access token retrieval, caching, and automatic refresh
    for Adobe CJA API requests.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize OAuth client with settings.

        Args:
            settings: Application settings containing Adobe credentials.
        """
        self.settings = settings
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0.0

    def _is_token_valid(self) -> bool:
        """Check if cached token is still valid.

        Returns:
            bool: True if token exists and hasn't expired.
        """
        if not self._access_token:
            return False
        # Add 60 second buffer before actual expiry
        return time.time() < (self._token_expiry - 60)

    async def get_access_token(self) -> str:
        """Get valid access token, refreshing if necessary.

        Returns:
            str: Valid Adobe IMS access token.

        Raises:
            httpx.HTTPError: If token request fails.
            ValueError: If response doesn't contain access_token.
        """
        if self._is_token_valid():
            assert self._access_token is not None  # For type checker
            return self._access_token

        return await self._fetch_new_token()

    async def _fetch_new_token(self) -> str:
        """Fetch new access token from Adobe IMS.

        Returns:
            str: Fresh access token.

        Raises:
            httpx.HTTPError: If token request fails.
            ValueError: If response doesn't contain access_token or expires_in.
        """
        token_url = self.settings.get_ims_token_url()

        # Prepare form data for OAuth 2.0 client credentials grant
        form_data = {
            "grant_type": "client_credentials",
            "client_id": self.settings.adobe_client_id,
            "client_secret": self.settings.adobe_client_secret,
            "scope": "openid,AdobeID,read_organizations,additional_info.projectedProductContext",
        }

        async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
            response = await client.post(
                token_url,
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()

        token_data = response.json()

        if "access_token" not in token_data:
            raise ValueError("Response missing 'access_token' field")

        self._access_token = token_data["access_token"]

        # Calculate token expiry (default to TTL from settings if not provided)
        expires_in = token_data.get("expires_in", self.settings.token_cache_ttl)
        self._token_expiry = time.time() + expires_in

        return self._access_token

    async def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for CJA API requests.

        Returns:
            dict: Headers including Authorization, x-api-key, and x-gw-ims-org-id.

        Raises:
            httpx.HTTPError: If token retrieval fails.
        """
        access_token = await self.get_access_token()

        return {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.settings.adobe_client_id,
            "x-gw-ims-org-id": self.settings.adobe_org_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def invalidate_token(self) -> None:
        """Invalidate cached token to force refresh on next request."""
        self._access_token = None
        self._token_expiry = 0.0
