"""MCP tool for generating status reports from multiple tests.

This module implements the generate_status_report tool following the service
layer pattern (ADR-006). The tool is a thin wrapper that:
1. Validates input with Pydantic/Literal types
2. Extracts dependencies from server context (ADR-007)
3. Delegates to ReportService
4. Converts exceptions to user-friendly error format
"""

from typing import Any, Literal

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field, field_validator

from testio_mcp.exceptions import TestIOAPIError, TestNotFoundException
from testio_mcp.server import mcp
from testio_mcp.services.report_service import ReportService
from testio_mcp.utilities import get_service
from testio_mcp.validators import coerce_to_int_list


# Pydantic Input Validation (AC2)
class GenerateStatusReportInput(BaseModel):
    """Input model for generate_status_report tool."""

    test_ids: list[int] = Field(
        ...,
        description="List of test IDs to include in report (e.g., [109363, 109364])",
        min_length=1,
        max_length=20,
        examples=[[109363, 109364]],
    )
    format: Literal["markdown", "text", "json"] = Field(
        default="markdown",
        description="Output format for the report",
    )

    @field_validator("test_ids", mode="before")
    @classmethod
    def coerce_and_validate_test_ids(cls, v: Any) -> list[int]:
        """Coerce test_ids to list[int] and validate constraints."""
        # Coerce to list[int] first
        test_ids = coerce_to_int_list(v)

        # Then validate constraints
        if not test_ids:
            raise ValueError("test_ids cannot be empty")
        if len(test_ids) > 20:
            raise ValueError("Maximum 20 test IDs allowed per report")
        if any(tid <= 0 for tid in test_ids):
            raise ValueError("All test IDs must be positive integers")
        return test_ids


# MCP Tool (AC1)
@mcp.tool()
async def generate_status_report(
    test_ids: list[int],
    format: Literal["markdown", "text", "json"] = "markdown",
    ctx: Context | None = None,
) -> str | dict[str, Any]:
    """Generate executive summary report from multiple tests.

    Includes metrics, critical issues, and progress overview.
    """
    # Validate input (AC2)
    input_model = GenerateStatusReportInput(test_ids=test_ids, format=format)

    # Validate context parameter
    if ctx is None:
        raise ToolError(
            "❌ Context is required\n"
            "ℹ️  FastMCP context injection failed\n"
            "💡 This is an internal error - please contact support"
        )

    # Create service instance using helper (eliminates 5 lines of boilerplate)
    service = get_service(ctx, ReportService)

    # Delegate to service and convert exceptions to MCP error format (AC8)
    try:
        result = await service.generate_report(
            test_ids=input_model.test_ids,
            format=input_model.format,
        )
        return result

    except ValueError as e:
        # Convert ValueError to ToolError with user-friendly message
        raise ToolError(
            f"❌ {str(e)}\n"
            f"ℹ️  Failed to generate status report\n"
            f"💡 Verify test IDs using list_tests tool"
        ) from e

    except TestNotFoundException as e:
        # Handle test not found (should be caught by service but handle defensively)
        raise ToolError(
            f"❌ Test ID '{e.test_id}' not found\n"
            f"ℹ️  The test may have been deleted, archived, or you may not have access to it\n"
            f"💡 Verify the test ID is correct and the test still exists"
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
            f"ℹ️  An unexpected error occurred while generating report\n"
            f"💡 Please try again or contact support if the problem persists"
        ) from e
