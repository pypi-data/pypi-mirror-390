"""Cache management and monitoring tools.

These tools provide administrative capabilities for cache management:
- get_cache_stats: Monitor cache performance metrics
- clear_cache: Clear all cached data for testing or manual refresh

Tools are auto-discovered and registered via ADR-011 pattern.
"""

from typing import Any, cast

from fastmcp import Context

from testio_mcp.server import ServerContext, mcp


@mcp.tool()
async def get_cache_stats(ctx: Context) -> dict[str, Any]:
    """Get cache performance metrics including hit rate, total requests, and entry count."""
    # Access cache from lifespan context (ADR-007)
    lifespan_ctx = cast(ServerContext, ctx.request_context.lifespan_context)
    cache = lifespan_ctx["cache"]

    return await cache.get_stats()


@mcp.tool()
async def clear_cache(ctx: Context) -> dict[str, str]:
    """Clear all cached data and reset statistics. Use for testing or manual data refresh."""
    lifespan_ctx = cast(ServerContext, ctx.request_context.lifespan_context)
    cache = lifespan_ctx["cache"]

    await cache.clear()

    return {
        "status": "success",
        "message": "Cache cleared successfully. All subsequent queries will hit the API.",
    }
