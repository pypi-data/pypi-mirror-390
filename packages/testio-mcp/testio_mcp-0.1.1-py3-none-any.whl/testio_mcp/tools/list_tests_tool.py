"""MCP tool for listing tests with status filtering.

This module implements the list_tests tool following the service
layer pattern (ADR-006). The tool is a thin wrapper that:
1. Validates input with Pydantic
2. Extracts dependencies from server context (ADR-007)
3. Delegates to ProductService
4. Converts exceptions to user-friendly error format
"""

from enum import Enum
from typing import Annotated, Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field

from testio_mcp.exceptions import ProductNotFoundException, TestIOAPIError
from testio_mcp.server import mcp
from testio_mcp.services.product_service import ProductService
from testio_mcp.utilities import get_service

# Enums (STORY-018 AC4)


class TestStatus(str, Enum):
    """Test lifecycle status.

    Statuses represent different stages of test execution:
    - running: Test currently active, bugs being reported
    - locked: Test finalized, no new bugs accepted
    - archived: Test completed and archived
    - customer_finalized: Customer marked as final
    - initialized: Test created but not yet started
    - cancelled: Test cancelled before completion
    """

    RUNNING = "running"
    LOCKED = "locked"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"
    CUSTOMER_FINALIZED = "customer_finalized"
    INITIALIZED = "initialized"


# Pydantic Models (AC2, AC6)


class TestSummary(BaseModel):
    """Summary information for a single test.

    Attributes:
        test_id: Unique test identifier (integer from API)
        title: Test title/name
        goal: Test goal/objective (optional)
        status: Current test status
        review_status: Review status (optional)
        testing_type: Type of testing (rapid, focused, coverage, usability)
        duration: Test duration in minutes (optional)
        starts_at: Test start timestamp (optional)
        ends_at: Test end timestamp (optional)
        bug_count: Bug count summary (only if include_bug_counts=True)
    """

    __test__ = False

    test_id: int = Field(description="Test ID (integer from API)")
    title: str = Field(description="Test title")
    goal: str | None = Field(default=None, description="Test goal/objective")
    status: str = Field(description="Test status (running, locked, archived, etc.)")
    review_status: str | None = Field(default=None, description="Review status (if applicable)")
    testing_type: str = Field(description="Testing type: rapid, focused, coverage, or usability")
    duration: int | None = Field(default=None, description="Test duration in minutes")
    starts_at: str | None = Field(default=None, description="Test start timestamp")
    ends_at: str | None = Field(default=None, description="Test end timestamp")
    bug_count: dict[str, Any] | None = Field(
        default=None, description="Bug count summary (only if include_bug_counts=True)"
    )


class ProductInfoSummary(BaseModel):
    """Product information summary."""

    id: int = Field(description="Product ID (integer from API)")
    name: str = Field(description="Product name")
    type: str = Field(description="Product type")


class ListTestsOutput(BaseModel):
    """Complete output for list_tests tool.

    This is the primary output model combining product info with
    filtered test summaries and optional bug counts.
    """

    product: ProductInfoSummary = Field(description="Product information for context")
    statuses_filter: list[str] = Field(description="Statuses that were used to filter tests")
    total_tests: int = Field(description="Total number of tests returned", ge=0)
    tests: list[TestSummary] = Field(description="List of test summaries")


# MCP Tool (AC1)


@mcp.tool()
async def list_tests(
    product_id: Annotated[
        int,
        Field(
            gt=0,
            description="Product ID from TestIO (e.g., 25073). Use list_products to find IDs.",
        ),
    ],
    ctx: Context,
    statuses: Annotated[
        list[TestStatus] | None,
        Field(
            description=(
                "Filter tests by lifecycle status. Filters applied client-side after API fetch. "
                "Omit to return all tests. "
                "Common filters: ['running'] for active, "
                "['archived', 'locked', 'customer_finalized'] for completed."
            ),
            json_schema_extra={"examples": [["running"], ["archived", "locked"]]},
        ),
    ] = None,
    include_bug_counts: Annotated[
        bool,
        Field(
            description=(
                "Include bug count summaries for each test. "
                "Adds 1-2s latency for products with 50+ tests. "
                "Omit for faster queries when counts not needed."
            ),
        ),
    ] = False,
) -> dict[str, Any]:
    """List tests for a product with status filtering. Optionally includes bug count summaries."""
    # Create service instance using helper (eliminates 5 lines of boilerplate)
    service = get_service(ctx, ProductService)

    # Delegate to service and convert exceptions to MCP error format (AC7)
    try:
        # Service handles enum extraction (STORY-018 AC4)
        # Cast to satisfy mypy - TestStatus is an Enum so this is safe
        from enum import Enum

        statuses_cast: list[str | Enum] | None = statuses  # type: ignore[assignment]
        service_result = await service.list_tests(
            product_id=product_id,
            statuses=statuses_cast,
            include_bug_counts=include_bug_counts,
        )

        # Transform service result to tool output format (keep IDs as integers)
        product = service_result["product"]
        tests = service_result["tests"]
        statuses_filter = service_result[
            "statuses_filter"
        ]  # AC8 - Use effective statuses from service
        bug_counts = service_result.get("bug_counts", {})

        # Build test summaries with optional bug counts
        test_summaries = []
        for test in tests:
            test_id = test["id"]  # Keep as integer from API
            summary = TestSummary(
                test_id=test_id,
                title=test["title"],
                goal=test.get("goal"),
                status=test["status"],
                review_status=test.get("review_status"),
                testing_type=test["testing_type"],
                duration=test.get("duration"),
                starts_at=test.get("starts_at"),
                ends_at=test.get("ends_at"),
                bug_count=bug_counts.get(str(test_id)) if include_bug_counts else None,
            )
            test_summaries.append(summary)

        # STORY-008 AC7: Empty results guidance
        if len(test_summaries) == 0:
            import logging

            logger = logging.getLogger(__name__)
            status_desc = "with specified filters" if statuses else "for this product"
            logger.info(
                f"ℹ️  No tests found {status_desc}\n"
                f"💡 Try removing status filters or check other products using list_products"
            )

        # Build validated output
        output = ListTestsOutput(
            product=ProductInfoSummary(
                id=product["id"],  # Keep as integer from API
                name=product["name"],
                type=product["type"],
            ),
            statuses_filter=statuses_filter,  # AC8 - Use effective statuses from service
            total_tests=len(test_summaries),
            tests=test_summaries,
        )

        return output.model_dump(by_alias=True, exclude_none=True)

    except ProductNotFoundException as e:
        # Convert domain exception to ToolError with user-friendly message
        raise ToolError(
            f"❌ Product ID '{e.product_id}' not found\n"
            f"ℹ️  This product may not exist or you don't have access to it\n"
            f"💡 Use the list_products tool to see available products"
        ) from e

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
            f"ℹ️  An unexpected error occurred while listing tests\n"
            f"💡 Please try again or contact support if the problem persists"
        ) from e
