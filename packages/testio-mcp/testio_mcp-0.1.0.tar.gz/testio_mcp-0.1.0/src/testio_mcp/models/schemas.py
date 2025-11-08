"""
Pydantic data models for TestIO API responses.

These models provide type-safe representations of TestIO API data
with validation and serialization support.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Product(BaseModel):
    """TestIO product representation.

    Products represent different testing offerings available
    through the TestIO platform.
    """

    id: int = Field(description="Unique product identifier")
    name: str = Field(description="Product name")
    description: str | None = Field(default=None, description="Product description")
    # Additional fields can be added as needed based on API responses


class HealthCheckResponse(BaseModel):
    """Response model for health_check tool.

    Used to validate and document the health check response structure.
    """

    authenticated: bool = Field(description="Whether API authentication succeeded")
    products_count: int = Field(description="Number of products retrieved")
    products: list[dict[str, Any]] = Field(
        description="List of product objects",
        default_factory=list,
    )
    message: str = Field(description="Human-readable status message")
    error: str | None = Field(default=None, description="Error message if check failed")


# Bug Models (Story-004)


class BugDevice(BaseModel):
    """Device information where a bug was found."""

    device_name: str = Field(description="Device model name")
    os_name: str = Field(description="Operating system name")
    os_version: str = Field(description="OS version")


class BugAttachment(BaseModel):
    """Attachment associated with a bug (screenshot, video, etc.)."""

    id: str = Field(description="Attachment ID")
    url: str = Field(description="Attachment URL")
    type: str = Field(description="Attachment type (screenshot, video, etc.)")


class BugDetails(BaseModel):
    """Detailed bug information with classification and metadata.

    This model represents a bug with all its details, including the
    derived bug_type and severity_level fields that handle the overloaded
    severity field from the TestIO API.
    """

    id: str = Field(description="Bug ID")
    title: str = Field(description="Bug title")
    bug_type: str = Field(
        description="Derived bug type: functional|visual|content|custom",
    )
    severity_level: str | None = Field(
        default=None,
        description=(
            "Severity level for functional bugs: low|high|critical. "
            "None for visual/content/custom bugs."
        ),
    )
    status: str = Field(
        description="Bug workflow status: accepted|rejected|new|known|fixed",
    )
    location: str | None = Field(
        default=None,
        description="URL or location where bug occurs",
    )
    expected_result: str | None = Field(
        default=None,
        description="Expected behavior",
    )
    actual_result: str | None = Field(
        default=None,
        description="Actual behavior observed",
    )
    steps: list[str] = Field(
        default_factory=list,
        description="Steps to reproduce",
    )
    author_name: str = Field(description="Bug reporter name")
    tester_name: str | None = Field(
        default=None,
        description="Tester who found the bug",
    )
    devices: list[BugDevice] = Field(
        default_factory=list,
        description="Devices where bug was found",
    )
    attachments: list[BugAttachment] = Field(
        default_factory=list,
        description="Screenshots, videos, etc.",
    )
    known: bool = Field(description="Whether bug is marked as known issue")
    exported_at: datetime | None = Field(
        default=None,
        description="When bug was exported to issue tracker",
    )
    created_at: datetime = Field(description="When bug was created")
    report_content: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Custom report structured content for custom bugs (accessibility, "
            "purchase reports, etc.). Contains a 'data' array with report-specific "
            "fields like WCAG checkpoints, recommendations, code snippets. "
            "Example: {'data': [{'key': 'wcag_checkpoints', 'value': '1.2.2, 1.4.3'}]}"
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_non_functional_bug_nulls(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Convert null list fields to empty lists for non-functional bugs only.

        Custom, visual, and content bugs return null for steps, devices, and
        attachments fields from the TestIO API. Functional bugs (with severity
        low/high/critical) should have actual data, so we only normalize nulls
        for non-functional types to avoid masking data quality issues.

        Args:
            data: Raw bug data from API before Pydantic validation

        Returns:
            Normalized bug data with empty lists for non-functional bug nulls
        """
        # Check bug_type field (derived from API's severity field)
        bug_type = data.get("bug_type", "")

        # Only normalize for non-functional bug types
        if bug_type in ["custom", "visual", "content"]:
            for field in ["steps", "devices", "attachments"]:
                if data.get(field) is None:
                    data[field] = []

        return data
