"""MCP tool for getting exploratory test bugs with advanced filtering.

This module implements the get_test_bugs tool following the service
layer pattern (ADR-006). The tool is a thin wrapper that:
1. Validates input with Pydantic/Literal types and Enums
2. Validates filter combinations early (e.g., severity only works with functional bugs)
3. Extracts dependencies from server context (ADR-007)
4. Delegates to BugService
5. Converts exceptions to user-friendly error format
"""

from enum import Enum
from typing import Annotated, Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field, field_validator

from testio_mcp.exceptions import TestIOAPIError, TestNotFoundException
from testio_mcp.server import mcp
from testio_mcp.services.bug_service import BugService
from testio_mcp.utilities import get_service
from testio_mcp.validators import coerce_to_int

# Input validation models


class GetTestBugsInput(BaseModel):
    """Input validation for get_test_bugs tool.

    Accepts test_id and page_size as int or string, coerces to int for validation.
    """

    test_id: int = Field(
        gt=0,
        description="Test ID from TestIO (e.g., 109363). Use list_tests to discover IDs.",
    )
    page_size: int = Field(
        ge=1,
        le=1000,
        default=100,
        description="Results per page (1-1000). Default 100. Lower values = faster.",
    )

    @field_validator("test_id", "page_size", mode="before")
    @classmethod
    def coerce_integers(cls, v: Any) -> int:
        """Coerce integer fields from string to int if needed."""
        return coerce_to_int(v)


# Enum types for filter validation
class BugType(str, Enum):
    """Bug type classification based on API severity field."""

    FUNCTIONAL = "functional"
    VISUAL = "visual"
    CONTENT = "content"
    CUSTOM = "custom"
    ALL = "all"


class BugSeverity(str, Enum):
    """Bug severity levels (functional bugs only)."""

    LOW = "low"
    HIGH = "high"
    CRITICAL = "critical"
    ALL = "all"


class BugStatus(str, Enum):
    """Bug workflow status."""

    ACCEPTED = "accepted"
    AUTO_ACCEPTED = "auto_accepted"
    REJECTED = "rejected"
    FORWARDED = "forwarded"
    ALL = "all"


@mcp.tool()
async def get_test_bugs(
    test_id: Annotated[
        int,
        Field(
            gt=0,
            description="Test ID from TestIO (e.g., 109363). Use list_tests to discover IDs.",
        ),
    ],
    bug_type: BugType = Field(  # noqa: B008
        default=BugType.ALL,
        description=(
            "Filter by bug type: functional (supports severity), visual, content, "
            "custom (optional config ID for refinement), all"
        ),
        json_schema_extra={"examples": ["functional", "visual", "custom", "all"]},
    ),
    severity: BugSeverity = Field(  # noqa: B008
        default=BugSeverity.ALL,
        description="Filter by severity (functional bugs only): low, high, critical, all",
        json_schema_extra={"examples": ["critical", "high", "all"]},
    ),
    status: BugStatus = Field(  # noqa: B008
        default=BugStatus.ALL,
        description=("Filter by bug status: accepted, rejected, forwarded, auto_accepted, all"),
        json_schema_extra={"examples": ["accepted", "rejected", "all"]},
    ),
    page_size: Annotated[
        int,
        Field(
            ge=1,
            le=1000,
            description="Results per page (1-1000). Default 100. Lower values = faster.",
        ),
    ] = 100,
    continuation_token: str | None = None,
    custom_report_config_id: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get bug details with filtering by type, severity, and status.

    Supports pagination for tests with many bugs. Use filters to narrow results
    by bug classification, workflow status, or custom report type."""
    # Validate and coerce input (accepts string or int for test_id and page_size)
    try:
        validated_input = GetTestBugsInput(test_id=test_id, page_size=page_size)
        test_id = validated_input.test_id
        page_size = validated_input.page_size
    except ValueError as e:
        raise ToolError(
            f"❌ Invalid input: {e}\n"
            f"ℹ️  test_id and page_size must be positive integers\n"
            f"💡 Use integers like 1216 or strings like '1216', not decimals"
        ) from e

    # Validate context parameter
    if ctx is None:
        raise ValueError("Context is required")

    # Normalize all enum parameters - Field may pass actual value or FieldInfo object
    # When not provided, Pydantic passes FieldInfo; extract its default value
    from pydantic.fields import FieldInfo

    # Normalize bug_type
    if isinstance(bug_type, FieldInfo):
        bug_type_value = bug_type.default if hasattr(bug_type, "default") else BugType.ALL
    elif isinstance(bug_type, BugType):
        bug_type_value = bug_type
    else:
        bug_type_value = BugType.ALL

    # Normalize severity
    if isinstance(severity, FieldInfo):
        severity_value = severity.default if hasattr(severity, "default") else BugSeverity.ALL
    elif isinstance(severity, BugSeverity):
        severity_value = severity
    else:
        severity_value = BugSeverity.ALL

    # Normalize status
    if isinstance(status, FieldInfo):
        status_value = status.default if hasattr(status, "default") else BugStatus.ALL
    elif isinstance(status, BugStatus):
        status_value = status
    else:
        status_value = BugStatus.ALL

    # Rule 0: continuation_token is self-sufficient - filters MUST NOT be provided
    # (STORY-017: Self-sufficient continuation tokens)
    if continuation_token is not None:
        # Check if any filter parameter was explicitly provided (non-default)
        filter_provided = (
            bug_type_value != BugType.ALL
            or severity_value != BugSeverity.ALL
            or status_value != BugStatus.ALL
            or custom_report_config_id is not None
        )
        if filter_provided:
            raise ToolError(
                "❌ Invalid parameter combination\n"
                "ℹ️ continuation_token is self-sufficient and cannot be used with filters\n"
                "💡 When using continuation_token, omit bug_type, severity, status, "
                "and custom_report_config_id parameters"
            )

    # Rule 1: severity parameter ONLY works with bug_type="functional"
    # Only validate if severity is explicitly NOT "all" (i.e., user is filtering by severity)
    if (
        bug_type_value in (BugType.VISUAL, BugType.CONTENT, BugType.CUSTOM, BugType.ALL)
        and severity_value != BugSeverity.ALL
    ):
        raise ToolError(
            f"❌ Invalid severity parameter\n"
            f"ℹ️ Severity filter cannot be used with bug_type='{bug_type_value.value}'\n"
            f"💡 Severity levels only apply to functional bugs. "
            f"Remove severity parameter or use bug_type='functional'"
        )

    # Rule 2: custom_report_config_id is OPTIONAL refinement for bug_type="custom"
    # If provided with bug_type="custom", filter to specific custom report type
    # If omitted with bug_type="custom", return ALL custom bugs (most common use case)
    # This follows the 99% use case: users want "all custom bugs" without knowing config IDs

    # Rule 3: custom_report_config_id ONLY works with bug_type="custom"
    # It's a refinement filter specific to custom bugs
    if custom_report_config_id is not None and bug_type_value != BugType.CUSTOM:
        raise ToolError(
            "❌ Invalid custom_report_config_id parameter\n"
            "ℹ️ custom_report_config_id can only be used with bug_type='custom'\n"
            "💡 Remove custom_report_config_id or set bug_type='custom'"
        )

    # Create service instance using helper (eliminates 5 lines of boilerplate)
    service = get_service(ctx, BugService)

    # Delegate to service and convert exceptions to MCP error format
    # CRITICAL: Pass enum.value to service (not Enum instances)
    try:
        result = await service.get_test_bugs(
            test_id=test_id,
            bug_type=bug_type_value.value,  # ← .value extracts string from normalized enum
            severity=severity_value.value,  # ← .value extracts string from normalized enum
            status=status_value.value,  # ← .value extracts string from normalized enum
            page_size=page_size,
            continuation_token=continuation_token,
            custom_report_config_id=custom_report_config_id,
        )

        # STORY-008 AC7: Empty results guidance
        filtered_count = result.get("filtered_count", 0)
        if filtered_count == 0:
            import logging

            logger = logging.getLogger(__name__)
            filter_desc = []
            if bug_type_value != BugType.ALL:
                filter_desc.append(f"type={bug_type_value.value}")
            if severity_value != BugSeverity.ALL:
                filter_desc.append(f"severity={severity_value.value}")
            if status_value != BugStatus.ALL:
                filter_desc.append(f"status={status_value.value}")

            filter_str = " with filters: " + ", ".join(filter_desc) if filter_desc else ""
            logger.info(
                f"ℹ️  No bugs found for test '{test_id}'{filter_str}\n"
                f"💡 Try removing filters or check that the test has been run"
            )

        # Add warning if results are truncated (first page with more results)
        if result.get("has_more") and continuation_token is None:
            page_size_actual = result.get("page_size", 0)
            if filtered_count > page_size_actual:
                # Note: We can't use print() in MCP tools - errors are returned as dicts
                # The AI client will see has_more=true and continuation_token
                pass

        return result

    except TestNotFoundException as e:
        # Convert domain exception to ToolError with user-friendly message
        raise ToolError(
            f"❌ Test ID '{e.test_id}' not found\n"
            f"ℹ️  This test may not exist or you don't have access\n"
            f"💡 Use list_tests to verify test IDs"
        ) from e

    except TestIOAPIError as e:
        # Convert API error to ToolError with user-friendly message
        raise ToolError(
            f"❌ API error ({e.status_code}): {e.message}\n"
            f"ℹ️  The TestIO API encountered an error\n"
            f"💡 Try again in a moment or check API status"
        ) from e

    except ValueError as e:
        # Convert validation error to ToolError with user-friendly message
        raise ToolError(
            f"❌ Validation error: {str(e)}\n"
            f"ℹ️  Invalid input parameters provided\n"
            f"💡 Check your parameters and try again"
        ) from e

    except Exception as e:
        # Catch-all for unexpected errors
        raise ToolError(
            f"❌ Unexpected error: {str(e)}\n"
            f"ℹ️  An unexpected error occurred while fetching bugs\n"
            f"💡 Please try again or contact support if the problem persists"
        ) from e
