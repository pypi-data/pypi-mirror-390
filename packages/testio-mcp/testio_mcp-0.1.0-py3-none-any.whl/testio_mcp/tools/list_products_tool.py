"""MCP tool for listing products.

This module implements the list_products tool following the service
layer pattern (ADR-006). The tool is a thin wrapper that:
1. Validates input with Pydantic
2. Extracts dependencies from server context (ADR-007)
3. Delegates to ProductService
4. Converts exceptions to user-friendly error format
"""

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field, field_validator

from testio_mcp.exceptions import TestIOAPIError
from testio_mcp.server import mcp
from testio_mcp.services.product_service import ProductService
from testio_mcp.utilities import get_service

# Pydantic Models


class ProductSummary(BaseModel):
    """Summary information for a product.

    Attributes:
        product_id: Unique product identifier (integer, matches API)
        name: Product name
        type: Product type (e.g., 'website', 'mobile')
        description: Product description (optional)
    """

    product_id: int = Field(description="Product ID", alias="id")
    name: str = Field(description="Product name")
    type: str = Field(description="Product type (e.g., 'website', 'mobile')")
    description: str | None = Field(
        default=None,
        description="Product description",
    )

    @field_validator("product_id", mode="before")
    @classmethod
    def coerce_id_to_int(cls, v: Any) -> int:
        """Convert product ID to integer (accepts string or int input).

        Args:
            v: Product ID value (int or str)

        Returns:
            Product ID as integer

        Raises:
            ValueError: If value cannot be converted to integer
        """
        return int(v)


class ListProductsOutput(BaseModel):
    """Output model for list_products tool.

    Attributes:
        total_count: Total number of products after filtering
        filters_applied: Dictionary of filters that were applied
        products: List of product summaries
    """

    total_count: int = Field(
        description="Total number of products after filtering",
        ge=0,
    )
    filters_applied: dict[str, str | None] = Field(
        description="Filters applied (search, product_type)",
    )
    products: list[ProductSummary] = Field(
        description="List of products with id, name, type, description",
    )


# MCP Tool


@mcp.tool()
async def list_products(
    ctx: Context,
    search: str | None = None,
    product_type: str | None = None,
) -> dict[str, Any]:
    """List all products with optional search and type filtering.

    Use to discover product IDs for other tools.
    """
    # Create service instance using helper (eliminates 5 lines of boilerplate)
    service = get_service(ctx, ProductService)

    # Delegate to service and convert exceptions to MCP error format
    try:
        result = await service.list_products(
            search=search,
            product_type=product_type,
        )

        # Validate output with Pydantic
        # This ensures API response matches expected structure
        validated = ListProductsOutput(**result)
        return validated.model_dump(by_alias=True, exclude_none=True)

    except TestIOAPIError as e:
        # Convert API error to ToolError with user-friendly message
        raise ToolError(
            f"❌ API error: {e.message}\n"
            f"ℹ️  HTTP status code: {e.status_code}\n"
            f"💡 Check API status and authentication. If the problem persists, contact support."
        ) from e

    except Exception as e:
        # Catch-all for unexpected errors
        raise ToolError(
            f"❌ Unexpected error: {str(e)}\n"
            f"ℹ️  An unexpected error occurred while fetching products\n"
            f"💡 Please try again or contact support if the problem persists"
        ) from e
