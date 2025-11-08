"""Helper functions for service instantiation with dependency injection.

This module provides utilities to reduce boilerplate in MCP tool implementations
by centralizing the dependency extraction and service instantiation pattern.
"""

from typing import TYPE_CHECKING, cast

from fastmcp import Context

from testio_mcp.services.base_service import BaseService

if TYPE_CHECKING:
    from testio_mcp.server import ServerContext


def get_service[ServiceT: BaseService](ctx: Context, service_class: type[ServiceT]) -> ServiceT:
    """Extract dependencies from FastMCP context and create service instance.

    This helper reduces tool boilerplate from 5 lines to 1 line while
    maintaining full type safety for mypy strict mode. It follows the
    dependency injection pattern established in ADR-007.

    Args:
        ctx: FastMCP context (injected automatically by framework)
        service_class: Service class to instantiate (must inherit BaseService)

    Returns:
        Service instance with injected client and cache dependencies

    Example:
        >>> @mcp.tool()
        >>> async def my_tool(param: str, ctx: Context) -> dict:
        ...     service = get_service(ctx, MyService)
        ...     return await service.my_method(param)

    Type Safety:
        >>> service = get_service(ctx, TestService)  # type: TestService
        >>> result = await service.get_test_status(123)  # type-checked!
    """
    # Extract dependencies from lifespan context (ADR-007)
    # Access via ctx.request_context.lifespan_context (FastMCP pattern)
    lifespan_ctx = cast("ServerContext", ctx.request_context.lifespan_context)
    client = lifespan_ctx["testio_client"]
    cache = lifespan_ctx["cache"]

    # Create and return service instance with injected dependencies
    return service_class(client=client, cache=cache)
