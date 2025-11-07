"""Configuration management for Aegis SDK."""

import os
from typing import Any

from pydantic import BaseModel, Field, SecretStr, field_validator


class AegisConfig(BaseModel):
    """Configuration for Aegis SDK.

    Supports both programmatic configuration and environment variable overrides.
    Environment variables take precedence over programmatic values.
    """

    base_url: str = Field(
        default="https://api.dev.aegis.cloudmatos.ai",
        description="Aegis Data Plane endpoint URL",
    )
    api_key: SecretStr = Field(description="Tenant API key for authentication")
    timeout_s: float = Field(
        default=10.0, ge=0.1, le=30.0, description="HTTP request timeout in seconds"
    )
    retries: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Number of retry attempts for failed requests",
    )
    user_agent: str = Field(
        default="aegis-python-sdk/0.1.1",
        description="User agent string for HTTP requests",
    )
    log_level: str = Field(
        default="info", description="Logging level (debug, info, warning, error)"
    )
    debug: bool = Field(
        default=False, description="Enable debug mode for print/log statements"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed = {"debug", "info", "warning", "error"}
        if v.lower() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.lower()

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")

    def __init__(self, **data: Any) -> None:
        """Initialize config with environment variable overrides."""
        # Apply environment variable overrides
        env_overrides: dict[str, Any] = {}

        if "AEGIS_BASE_URL" in os.environ:
            env_overrides["base_url"] = os.environ["AEGIS_BASE_URL"]

        if "AEGIS_API_KEY" in os.environ:
            env_overrides["api_key"] = os.environ["AEGIS_API_KEY"]

        if "AEGIS_TIMEOUT_S" in os.environ:
            try:
                env_overrides["timeout_s"] = float(os.environ["AEGIS_TIMEOUT_S"])
            except ValueError:
                pass  # Use default if invalid

        if "AEGIS_RETRIES" in os.environ:
            try:
                env_overrides["retries"] = int(os.environ["AEGIS_RETRIES"])
            except ValueError:
                pass  # Use default if invalid

        if "AEGIS_LOG_LEVEL" in os.environ:
            env_overrides["log_level"] = os.environ["AEGIS_LOG_LEVEL"]

        if "AEGIS_DEBUG" in os.environ:
            env_overrides["debug"] = os.environ["AEGIS_DEBUG"].lower() in (
                "true",
                "1",
                "yes",
                "on",
            )

        # Merge programmatic data with env overrides (env takes precedence)
        merged_data = {**data, **env_overrides}
        super().__init__(**merged_data)

    @property
    def api_key_plain(self) -> str:
        """Get the API key as plain text (use carefully, avoid logging)."""
        return self.api_key.get_secret_value()

    def model_dump_safe(self) -> dict[str, Any]:
        """Return config as dict with sensitive fields masked."""
        data = self.model_dump()
        if "api_key" in data:
            data["api_key"] = "***masked***"
        return data  # pragma: no cover
