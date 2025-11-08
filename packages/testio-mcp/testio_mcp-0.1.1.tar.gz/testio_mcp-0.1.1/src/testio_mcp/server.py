"""
FastMCP server for TestIO Customer API integration.

This module implements the Model Context Protocol server with:
- Shared TestIO API client instance
- Structured logging with token sanitization (AC14)
- Health check tool for authentication verification
- Lifespan handler for resource initialization/cleanup (ADR-007)
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from fastmcp import Context, FastMCP

from .cache import InMemoryCache
from .client import TestIOClient
from .config import settings


# Type-safe context for dependency injection (ADR-007)
class ServerContext(TypedDict):
    """Type definition for FastMCP app.context dictionary.

    This enables type-safe access to shared dependencies stored in
    the lifespan handler and accessed via Context parameter in tools.
    """

    testio_client: TestIOClient
    cache: InMemoryCache


# Configure structured logging (AC14)
class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging with token sanitization."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with structured fields.

        Args:
            record: Log record to format

        Returns:
            JSON string with log data
        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def configure_logging() -> None:
    """Configure structured logging based on settings.

    Sets up logging with:
    - JSON or text format based on LOG_FORMAT setting
    - Log level from LOG_LEVEL setting
    - Token sanitization via client event hooks
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.LOG_FORMAT.lower() == "json":
        formatter: logging.Formatter = JSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Configure package logger
    logger = logging.getLogger("testio_mcp")
    logger.setLevel(log_level)


# Configure logging on module load
configure_logging()

# Logger for server operations
logger = logging.getLogger(__name__)

# Shared resources (ADR-002: global concurrency control)
# Note: _testio_client and _cache moved to lifespan handler (ADR-007)
_global_semaphore: asyncio.Semaphore | None = None


def get_global_semaphore() -> asyncio.Semaphore:
    """Get or create the shared semaphore for global concurrency control (ADR-002).

    This semaphore is shared across all TestIOClient instances to enforce
    a global limit on concurrent API requests. This prevents overwhelming
    the TestIO API.

    For Story 1 (single client): provides concurrency control.
    For future stories (multiple products): ensures total concurrent requests
    across all products stays within limit.

    Returns:
        Shared semaphore instance with max_concurrent_requests limit
    """
    global _global_semaphore

    if _global_semaphore is None:
        _global_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_API_REQUESTS)
        logger.info(f"Created global semaphore with limit: {settings.MAX_CONCURRENT_API_REQUESTS}")

    return _global_semaphore


@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncIterator[ServerContext]:
    """Manage shared resources during server lifecycle (ADR-007).

    This lifespan handler follows FastMCP's Context injection pattern by
    initializing dependencies at startup and yielding them as a context object
    that tools can access via ctx.request_context.lifespan_context.

    Startup:
        - Create TestIOClient with connection pooling
        - Create InMemoryCache for response caching
        - Yield ServerContext for dependency injection

    Shutdown:
        - Automatically close TestIOClient via async context manager
        - Cache is garbage collected (no explicit cleanup needed)

    Architecture:
        - Single-tenant: Shared client/cache across all requests (current)
        - Multi-tenant: Will be extended in STORY-010 with ClientPool

    Reference:
        - ADR-007: FastMCP Context Injection Pattern
        - FastMCP docs: https://gofastmcp.com/servers/context
    """
    logger.info("Initializing server dependencies")

    # Get shared semaphore for global concurrency control (ADR-002)
    shared_semaphore = get_global_semaphore()

    # Create client with async context manager
    async with TestIOClient(
        base_url=settings.TESTIO_CUSTOMER_API_BASE_URL,
        api_token=settings.TESTIO_CUSTOMER_API_TOKEN,
        max_concurrent_requests=settings.MAX_CONCURRENT_API_REQUESTS,
        max_connections=settings.CONNECTION_POOL_SIZE,
        max_keepalive_connections=settings.CONNECTION_POOL_MAX_KEEPALIVE,
        timeout=settings.HTTP_TIMEOUT_SECONDS,
        semaphore=shared_semaphore,
    ) as client:
        # Create cache
        cache = InMemoryCache()

        logger.info("Server dependencies initialized (client, cache)")

        # Yield context for tools to access via ctx.request_context.lifespan_context
        yield ServerContext(testio_client=client, cache=cache)

        # Cleanup: Client closed automatically by context manager
        logger.info("Server dependencies cleaned up")


# Initialize FastMCP server with lifespan (ADR-007)
mcp = FastMCP("TestIO MCP Server", lifespan=lifespan)


# Tools registered below
# (get_testio_client and get_cache removed - replaced by Context injection, ADR-007)


@mcp.tool()
async def health_check(ctx: Context) -> dict[str, Any]:
    """Verify TestIO API authentication and connectivity.

    Returns product count as health indicator.
    Uses ProductService for consistency and caching benefits.
    """
    logger.info("Running health check")

    # Import here to avoid circular dependency with auto-discovery
    from .services.product_service import ProductService
    from .utilities import get_service

    # Create service instance (reuses service layer, benefits from caching)
    service = get_service(ctx, ProductService)

    try:
        # Use service layer to fetch products (benefits from caching)
        result = await service.list_products()

        product_count = result["total_count"]

        logger.info(f"Health check passed: {product_count} products available")

        return {
            "authenticated": True,
            "products_count": product_count,
            "message": f"Successfully authenticated. {product_count} products available.",
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "authenticated": False,
            "products_count": 0,
            "message": f"Authentication failed: {str(e)}",
            "error": str(e),
        }


# Auto-discover and register all tools (STORY-012 AC4, STORY-015)
# Uses pkgutil to find all modules in tools/ package
# Must be at end of file to avoid circular imports
import pkgutil  # noqa: E402

import testio_mcp.tools  # noqa: E402

# Discover all tool modules in the tools package
for module_info in pkgutil.iter_modules(testio_mcp.tools.__path__):
    # Import each tool module to trigger @mcp.tool() registration
    module_name = module_info.name
    __import__(f"testio_mcp.tools.{module_name}")
    logger.debug(f"Auto-discovered and registered tool module: {module_name}")

# Apply tool filtering based on configuration (STORY-015)
if settings.ENABLED_TOOLS is not None or settings.DISABLED_TOOLS is not None:
    all_tools = list(mcp._tool_manager._tools.keys())
    tools_to_remove = []

    for tool_name in all_tools:
        # Allowlist mode: Keep only tools in ENABLED_TOOLS
        if settings.ENABLED_TOOLS is not None:
            if tool_name not in settings.ENABLED_TOOLS:
                tools_to_remove.append(tool_name)
                logger.info(f"Filtering out tool (not in ENABLED_TOOLS): {tool_name}")
        # Denylist mode: Remove tools in DISABLED_TOOLS
        elif settings.DISABLED_TOOLS is not None:
            if tool_name in settings.DISABLED_TOOLS:
                tools_to_remove.append(tool_name)
                logger.info(f"Filtering out tool (in DISABLED_TOOLS): {tool_name}")

    # Remove filtered tools from registry
    for tool_name in tools_to_remove:
        del mcp._tool_manager._tools[tool_name]

    logger.info(f"Tool filtering complete: {len(tools_to_remove)} tools removed")

# Log total tools registered (access internal _tools dict)
tool_count = len(mcp._tool_manager._tools)
tool_names = list(mcp._tool_manager._tools.keys())
logger.info(f"Auto-discovery complete: {tool_count} tools registered: {tool_names}")
