"""MCP tool for getting exploratory test status.

This module implements the get_test_status tool following the service
layer pattern (ADR-006). The tool is a thin wrapper that:
1. Validates input with Pydantic
2. Extracts dependencies from server context (ADR-007)
3. Delegates to TestService
4. Converts exceptions to user-friendly error format
"""

from typing import Annotated, Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field, field_validator

from testio_mcp.exceptions import TestIOAPIError, TestNotFoundException
from testio_mcp.server import mcp
from testio_mcp.services.test_service import TestService
from testio_mcp.utilities import get_service
from testio_mcp.validators import coerce_to_int

# Pydantic Models (AC2-5)


class GetTestStatusInput(BaseModel):
    """Input validation for get_test_status tool.

    Accepts test_id as int or string, coerces to int for validation.
    """

    test_id: int = Field(
        gt=0,
        description="Test ID from TestIO (e.g., 109363). Use list_tests to find IDs.",
    )

    @field_validator("test_id", mode="before")
    @classmethod
    def coerce_test_id(cls, v: Any) -> int:
        """Coerce test_id from string to int if needed."""
        return coerce_to_int(v)


class BugSummary(BaseModel):
    """Bug summary statistics for a test.

    Attributes:
        total_count: Total number of bugs found in test
        by_severity: Bug count grouped by severity level
        by_status: Bug count grouped by bug status
        recent_bugs: List of 3 most recent bugs with basic info
    """

    total_count: int = Field(
        description="Total number of bugs found in test",
        ge=0,
    )
    by_severity: dict[str, int] = Field(
        description="Bug count grouped by severity (critical, high, low, visual, content)",
    )
    by_status: dict[str, int] = Field(
        description="Bug count grouped by status (accepted, rejected, new, known, fixed)",
    )
    recent_bugs: list[dict[str, Any]] = Field(
        description="3 most recent bugs with id, title, severity, status",
        max_length=3,
    )


class ProductInfo(BaseModel):
    """Product information embedded in test data."""

    id: int = Field(description="Product ID (integer from API)")
    name: str = Field(description="Product name")


class FeatureInfo(BaseModel):
    """Feature information embedded in test data."""

    id: int = Field(description="Feature ID (integer from API)")
    name: str = Field(description="Feature name")


class TestDetails(BaseModel):
    """Detailed information about an exploratory test."""

    id: int = Field(description="Test ID (integer from API)")
    title: str = Field(description="Test title")
    goal: str | None = Field(default=None, description="Test goal/objective")
    testing_type: str = Field(
        description="Testing type: rapid, focused, coverage, or usability",
    )
    duration: int | None = Field(default=None, description="Test duration in minutes")
    status: str = Field(
        description="Test status: locked, archived, running, review, etc.",
    )
    review_status: str | None = Field(
        default=None,
        description="Review status: review_successful, review_failed, etc.",
    )
    requirements: list[dict[str, Any]] | None = Field(
        default=None,
        description="Test requirements (list of requirement objects)",
    )
    created_at: str | None = Field(default=None, description="Creation timestamp")
    starts_at: str | None = Field(default=None, description="Start timestamp")
    ends_at: str | None = Field(default=None, description="End timestamp")
    product: ProductInfo = Field(description="Associated product information")
    feature: FeatureInfo | None = Field(
        default=None,
        description="Associated feature information (if applicable)",
    )


class TestStatusOutput(BaseModel):
    """Complete test status with configuration and bug summary.

    This is the primary output model for the get_test_status tool,
    combining test configuration details with aggregated bug statistics.
    """

    test: TestDetails = Field(description="Detailed test configuration and status")
    bugs: BugSummary = Field(description="Aggregated bug summary statistics")


# MCP Tool (AC1)


@mcp.tool()
async def get_test_status(
    test_id: Annotated[
        int,
        Field(
            gt=0,
            description="Test ID from TestIO (e.g., 109363). Use list_tests to find IDs.",
        ),
    ],
    ctx: Context,
) -> dict[str, Any]:
    """Get comprehensive test status.

    Includes configuration, bug summary, timeline, and review information.
    """
    # Validate and coerce input (accepts string or int)
    try:
        validated_input = GetTestStatusInput(test_id=test_id)
        test_id = validated_input.test_id
    except ValueError as e:
        raise ToolError(
            f"❌ Invalid test_id: {e}\n"
            f"ℹ️  test_id must be a positive integer\n"
            f"💡 Use an integer like 1216, not a string like '1216.5'"
        ) from e

    # Create service instance using helper (eliminates 5 lines of boilerplate)
    service = get_service(ctx, TestService)

    # Delegate to service and convert exceptions to MCP error format
    try:
        result = await service.get_test_status(test_id)

        # Validate output with Pydantic (optional but recommended)
        # This ensures API response matches expected structure
        validated = TestStatusOutput(**result)
        return validated.model_dump(by_alias=True, exclude_none=True)

    except TestNotFoundException:
        # Convert domain exception to ToolError with user-friendly message
        raise ToolError(
            f"❌ Test ID '{test_id}' not found\n"
            f"ℹ️  The test may have been deleted, archived, or you may not have access to it\n"
            f"💡 Verify the test ID is correct and the test still exists"
        ) from None

    except TestIOAPIError as e:
        # Convert API error to ToolError with user-friendly message
        raise ToolError(
            f"❌ API error: {e.message}\n"
            f"ℹ️  HTTP status code: {e.status_code}\n"
            f"💡 Check API status and try again. If the problem persists, contact support."
        ) from e

    except Exception as e:
        # Catch-all for unexpected errors
        raise ToolError(
            f"❌ Unexpected error: {str(e)}\n"
            f"ℹ️  An unexpected error occurred while fetching test status\n"
            f"💡 Please try again or contact support if the problem persists"
        ) from e
