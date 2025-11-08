"""MCP tool for querying test activity by timeframe.

This module implements the get_test_activity_by_timeframe tool following
the service layer pattern (ADR-006). The tool is a thin wrapper that:
1. Validates input with Pydantic
2. Extracts dependencies from server context (ADR-007)
3. Delegates to ActivityService
4. Converts exceptions to user-friendly error format
"""

from enum import Enum
from typing import Annotated, Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field, field_validator

from testio_mcp.exceptions import ProductNotFoundException, TestIOAPIError
from testio_mcp.server import mcp
from testio_mcp.services.activity_service import ActivityService
from testio_mcp.utilities import get_service, parse_flexible_date
from testio_mcp.validators import coerce_to_int_list

# Input validation models


class GetActivityByTimeframeInput(BaseModel):
    """Input validation for get_test_activity_by_timeframe tool.

    Accepts product_ids as various formats, coerces to list[int].
    """

    product_ids: list[int] = Field(
        min_length=1,
        max_length=100,
        description="Product IDs from TestIO (e.g., [25073, 598]).",
    )

    @field_validator("product_ids", mode="before")
    @classmethod
    def coerce_product_ids(cls, v: Any) -> list[int]:
        """Coerce product_ids to list[int] from various formats."""
        return coerce_to_int_list(v)


# Enums (STORY-018 AC4)


class TestDateField(str, Enum):
    """Test date field for timeframe filtering.

    Represents different test lifecycle timestamps:
    - created_at: When test was created in the system
    - start_at: When test execution started (testers began work)
    - end_at: When test execution ended (testing completed)
    - any: Any of the above timestamps fall within the range
    """

    CREATED_AT = "created_at"
    START_AT = "start_at"
    END_AT = "end_at"
    ANY = "any"


# Pydantic Models


class TestSummary(BaseModel):
    """Minimal test metadata for timeframe discovery."""

    id: int = Field(description="Test ID")
    title: str = Field(description="Test title")
    status: str = Field(description="Test status (running, locked, archived, etc.)")
    testing_type: str = Field(description="Testing type (rapid, focused, coverage, usability)")


class ProductActivity(BaseModel):
    """Product activity summary within a timeframe."""

    product_id: str = Field(description="Product ID")
    product_name: str = Field(description="Product name")
    tests_created: int = Field(description="Tests created in timeframe", ge=0)
    tests_started: int = Field(description="Tests started in timeframe", ge=0)
    tests_completed: int = Field(description="Tests completed in timeframe", ge=0)
    total_tests_in_range: int = Field(description="Total unique tests in timeframe", ge=0)
    testing_types: dict[str, int] = Field(
        description="Count by testing type (rapid, focused, coverage, usability, other)"
    )
    tests: list[TestSummary] = Field(
        description=(
            "Tests in this timeframe with minimal metadata (id, title, status, testing_type)"
        )
    )
    bug_count: int | None = Field(default=None, description="Bug count (if include_bugs=True)")


class TimeframeActivityOutput(BaseModel):
    """Complete timeframe activity output."""

    start_date: str = Field(description="Start date (YYYY-MM-DD)")
    end_date: str = Field(description="End date (YYYY-MM-DD)")
    days_in_range: int = Field(description="Number of days in range", ge=1)
    total_products: int = Field(description="Total products queried", ge=1)
    total_tests: int = Field(description="Total tests in timeframe", ge=0)
    overall_testing_types: dict[str, int] = Field(description="Overall testing type distribution")
    products: list[ProductActivity] = Field(description="Product-wise activity breakdown")
    timeline_data: dict[str, int] = Field(
        description="Tests grouped by week/month for visualization"
    )
    failed_products: list[str] = Field(
        default_factory=list, description="Product IDs that failed to load"
    )


# MCP Tool


@mcp.tool()
async def get_test_activity_by_timeframe(
    product_ids: Annotated[
        list[int],
        Field(
            min_length=1,
            max_length=100,
            description="Product IDs from TestIO (e.g., [25073, 598]).",
            json_schema_extra={"examples": [[25073, 598]]},
        ),
    ],
    start_date: Annotated[
        str,
        Field(
            description=(
                "Start date: ISO 8601 (YYYY-MM-DD), relative ('last 30 days'), "
                "or business term ('this quarter')"
            ),
            json_schema_extra={"examples": ["2024-01-01", "last 30 days", "this quarter"]},
        ),
    ],
    end_date: Annotated[
        str | None,
        Field(
            description=(
                "End date: ISO 8601 (YYYY-MM-DD), relative ('today'), "
                "or business term ('this month'). Defaults to 'today' if not specified."
            ),
            json_schema_extra={"examples": ["2024-12-31", "today", "this month"]},
        ),
    ] = None,
    date_field: Annotated[
        TestDateField,
        Field(
            description=(
                "Test lifecycle timestamp to filter by. 'start_at' filters by execution start. "
                "'created_at' filters by creation date. 'end_at' filters by completion date. "
                "'any' matches if any timestamp falls within range."
            ),
            json_schema_extra={"examples": ["start_at", "created_at", "any"]},
        ),
    ] = TestDateField.START_AT,
    include_bugs: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Query test activity across products within a date range.

    Filters by lifecycle timestamp and provides product breakdown, testing type
    distribution, and optional bug metrics.
    """
    # Validate and coerce input (accepts various formats for product_ids)
    try:
        validated_input = GetActivityByTimeframeInput(product_ids=product_ids)
        product_ids = validated_input.product_ids
    except ValueError as e:
        raise ToolError(
            f"❌ Invalid product_ids: {e}\n"
            f"ℹ️  product_ids must be a list of positive integers\n"
            f"💡 Use [54, 22] or ['54', '22'] or even 54 (single ID)"
        ) from e

    # Validate context parameter
    if ctx is None:
        raise ValueError("Context is required")

    # Parse flexible date inputs to ISO 8601 datetime strings
    # ToolError exceptions from parse_flexible_date() propagate automatically
    parsed_start_date = parse_flexible_date(start_date, start_of_day=True)
    parsed_end_date = parse_flexible_date(end_date or "today", start_of_day=False)

    # Extract date portion (YYYY-MM-DD) for service layer compatibility
    # Service layer expects YYYY-MM-DD format, not full ISO datetime
    start_date_only = parsed_start_date[:10]
    end_date_only = parsed_end_date[:10]

    # Create service instance using helper (eliminates 5 lines of boilerplate)
    service = get_service(ctx, ActivityService)

    # Delegate to service (business logic)
    try:
        result = await service.get_activity_by_timeframe(
            product_ids=product_ids,
            start_date=start_date_only,
            end_date=end_date_only,
            date_field=date_field,
            include_bugs=include_bugs,
        )

        # STORY-008 AC7: Empty results guidance
        total_tests = result.get("total_tests", 0)
        if total_tests == 0:
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                f"ℹ️  No test activity found for {len(product_ids)} product(s) "
                f"between {start_date} and {end_date}\n"
                f"💡 Try expanding the date range or checking different products"
            )

        # Validate output with Pydantic (optional but recommended)
        validated = TimeframeActivityOutput(**result)
        return validated.model_dump(by_alias=True, exclude_none=True)

    except ValueError as e:
        # Convert validation errors to ToolError with user-friendly message
        error_msg = str(e)
        formatted_error = error_msg if error_msg.startswith("❌") else f"❌ {error_msg}"
        raise ToolError(
            f"{formatted_error}\n"
            f"ℹ️  Failed to retrieve activity data\n"
            f"💡 Check date range, product IDs, and date_field value"
        ) from e

    except ProductNotFoundException as e:
        # Convert domain exception to ToolError with user-friendly message
        raise ToolError(
            f"❌ Product ID '{e.product_id}' not found\n"
            f"ℹ️  This product may not exist or you don't have access\n"
            f"💡 Use list_products tool to see available products"
        ) from e

    except TestIOAPIError as e:
        # Convert API error to ToolError with user-friendly message
        raise ToolError(
            f"❌ API error ({e.status_code}): {e.message}\n"
            f"ℹ️  The TestIO API encountered an error\n"
            f"💡 Try again in a moment or check API status"
        ) from e

    except Exception as e:
        # Catch-all for unexpected errors
        raise ToolError(
            f"❌ Unexpected error: {str(e)}\n"
            f"ℹ️  An unexpected error occurred while fetching activity data\n"
            f"💡 Please try again or contact support if the problem persists"
        ) from e
