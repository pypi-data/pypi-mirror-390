"""Configuration management for Adobe CJA MCP Server."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Note: Credentials are provided via Claude Desktop MCP configuration,
    not from a .env file. See README.md for configuration details.
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    # Adobe API Credentials
    adobe_client_id: str = Field(..., description="Adobe API Client ID")
    adobe_client_secret: str = Field(..., description="Adobe API Client Secret")
    adobe_org_id: str = Field(..., description="Adobe Organization ID")
    adobe_ims_host: str = Field(
        default="ims-na1.adobelogin.com",
        description="Adobe IMS authentication host",
    )
    adobe_cja_api_base: str = Field(
        default="https://cja.adobe.io",
        description="CJA API base URL",
    )
    adobe_data_view_id: str = Field(..., description="CJA Data View ID")

    # Optional settings
    token_cache_ttl: int = Field(
        default=3600,
        description="Access token cache TTL in seconds",
    )
    request_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of request retries",
    )

    @field_validator("adobe_org_id")
    @classmethod
    def validate_org_id(cls, v: str) -> str:
        """Ensure org ID has correct format."""
        if not v.endswith("@AdobeOrg"):
            raise ValueError("adobe_org_id must end with '@AdobeOrg'")
        return v

    @field_validator("adobe_cja_api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> str:
        """Ensure API base URL doesn't have trailing slash."""
        return v.rstrip("/")

    def get_ims_token_url(self) -> str:
        """Get the full IMS token endpoint URL."""
        return f"https://{self.adobe_ims_host}/ims/token/v3"

    def get_api_url(self, path: str) -> str:
        """Construct full API URL from path."""
        path = path.lstrip("/")
        return f"{self.adobe_cja_api_base}/{path}"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings loaded from environment.

    Raises:
        ValidationError: If required environment variables are missing or invalid.
    """
    return Settings()
