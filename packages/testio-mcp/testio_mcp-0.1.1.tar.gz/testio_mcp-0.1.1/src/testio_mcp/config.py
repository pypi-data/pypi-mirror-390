"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables with type validation.
"""

from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # TestIO API Configuration
    TESTIO_CUSTOMER_API_BASE_URL: str = Field(
        default="https://api.stage-a.space/customer/v2",
        description="TestIO Customer API base URL",
    )
    TESTIO_CUSTOMER_API_TOKEN: str = Field(
        ...,
        description="TestIO Customer API authentication token (required)",
    )

    # HTTP Client Configuration
    MAX_CONCURRENT_API_REQUESTS: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum concurrent API requests (semaphore limit)",
    )
    CONNECTION_POOL_SIZE: int = Field(
        default=20,
        ge=1,
        le=100,
        description="HTTP connection pool size",
    )
    CONNECTION_POOL_MAX_KEEPALIVE: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum connections to keep alive",
    )
    HTTP_TIMEOUT_SECONDS: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="HTTP request timeout in seconds",
    )
    MAX_ACQUIRE_TIMEOUT_SECONDS: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="Maximum time to wait for connection pool (prevents indefinite blocking)",
    )

    # Cache Configuration (TTLs in seconds)
    CACHE_TTL_PRODUCTS: int = Field(
        default=3600,
        ge=0,
        description="Cache TTL for products (1 hour default)",
    )
    CACHE_TTL_TESTS: int = Field(
        default=300,
        ge=0,
        description="Cache TTL for test data (5 minutes default)",
    )
    CACHE_TTL_BUGS: int = Field(
        default=60,
        ge=0,
        description="Cache TTL for bug data (1 minute default)",
    )

    # Pagination Configuration
    DEFAULT_PAGE_SIZE: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Default number of items per page",
    )
    MAX_PAGE_SIZE: int = Field(
        default=100,
        ge=1,
        le=200,
        description="Maximum allowed page size",
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format (json or text)",
    )

    # Auto-Acceptance Configuration (STORY-005c)
    AUTO_ACCEPTANCE_ALERT_THRESHOLD: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Alert when auto-acceptance rate exceeds this threshold (0.0-1.0). "
        "Auto-acceptance occurs when bugs timeout after 10 days without customer review. "
        "Default 0.20 (20%) indicates significant feedback loop degradation.",
    )

    # Tool Enable/Disable Configuration (STORY-015)
    ENABLED_TOOLS: str | list[str] | None = Field(
        default=None,
        description="Allowlist of tool names to enable (all others disabled). "
        "Tool names come from function names (e.g., 'get_test_status', 'list_products'). "
        "Accepts comma-separated string or JSON array. "
        "Cannot be used with DISABLED_TOOLS. Default: None (all tools enabled).",
    )
    DISABLED_TOOLS: str | list[str] | None = Field(
        default=None,
        description="Denylist of tool names to disable (all others enabled). "
        "Tool names come from function names (e.g., 'get_test_status', 'list_products'). "
        "Accepts comma-separated string or JSON array. "
        "Cannot be used with ENABLED_TOOLS. Default: None (no tools disabled).",
    )

    @field_validator("ENABLED_TOOLS", "DISABLED_TOOLS", mode="before")
    @classmethod
    def parse_tool_list(cls, v: Any) -> list[str] | None:
        """Parse tool list from comma-separated string or JSON array.

        Args:
            v: Raw value from environment variable

        Returns:
            Parsed list of tool names, or None if not set

        Examples:
            "health_check,list_products" -> ["health_check", "list_products"]
            '["health_check", "list_products"]' -> ["health_check", "list_products"]
            None -> None
        """
        if v is None:
            return None

        # If already a list (from JSON parsing), return as-is
        if isinstance(v, list):
            return v

        # Parse comma-separated string
        if isinstance(v, str):
            # Strip whitespace and filter empty strings
            return [tool.strip() for tool in v.split(",") if tool.strip()]

        # v is already list[str] or None from Pydantic's type coercion
        return None if v is None else v

    @model_validator(mode="after")
    def validate_tool_enablement_mutual_exclusion(self) -> "Settings":
        """Validate that ENABLED_TOOLS and DISABLED_TOOLS are mutually exclusive.

        Returns:
            The validated Settings instance

        Raises:
            ValueError: If both ENABLED_TOOLS and DISABLED_TOOLS are set
        """
        enabled = self.ENABLED_TOOLS
        disabled = self.DISABLED_TOOLS

        # Both None is OK (default behavior - all tools enabled)
        if enabled is None and disabled is None:
            return self

        # One or the other is OK
        if enabled is None or disabled is None:
            return self

        # Both set is an error
        raise ValueError(
            "ENABLED_TOOLS and DISABLED_TOOLS cannot be used simultaneously. "
            "Choose one approach: allowlist (ENABLED_TOOLS) or denylist (DISABLED_TOOLS)."
        )

        return self


def load_settings() -> Settings:
    """Load settings from environment with fallback for testing.

    Returns:
        Settings instance loaded from environment variables

    Note:
        With pydantic mypy plugin enabled, mypy understands that
        Settings() reads from environment variables, so no type
        ignores are needed.
    """
    try:
        return Settings()
    except Exception:
        # Fallback for testing environments without .env
        import os

        os.environ["TESTIO_CUSTOMER_API_TOKEN"] = "test_token_placeholder"
        return Settings()


# Global settings instance
settings = load_settings()
