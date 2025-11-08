"""Base service class providing common patterns for all services.

This module provides the BaseService class that eliminates boilerplate code
across service implementations by providing:
- Standard dependency injection constructor
- Cache key formatting helpers
- Cache-or-fetch pattern with 404 transformation and stampede protection
- Standardized TTL constants

Example:
    >>> class UserStoryService(BaseService):
    ...     async def get_user_story(self, user_story_id: int) -> dict:
    ...         return await self._get_cached_or_fetch(
    ...             cache_key=self._make_cache_key("user_story", user_story_id),
    ...             fetch_fn=lambda: self.client.get(f"user_stories/{user_story_id}"),
    ...             ttl_seconds=self.CACHE_TTL_USER_STORIES,
    ...             transform_404=UserStoryNotFoundException(user_story_id)
    ...         )
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from testio_mcp.cache import InMemoryCache
from testio_mcp.client import TestIOClient
from testio_mcp.config import settings
from testio_mcp.exceptions import TestIOAPIError


class BaseService:
    """Base class for all service layer classes.

    Provides common dependency injection pattern and cache helpers to eliminate
    boilerplate code across services.

    TTL Configuration:
        Cache TTL values are read from settings (environment variables) for
        consistency with ADR-004. This allows runtime configuration via .env
        file without code changes.

    Attributes:
        client: TestIO API client for making HTTP requests
        cache: In-memory cache for storing API responses
        CACHE_TTL_PRODUCTS: TTL for product data (from settings, default 1 hour)
        CACHE_TTL_TESTS: TTL for test data (from settings, default 5 minutes)
        CACHE_TTL_BUGS: TTL for bug data (from settings, default 1 minute)
        CACHE_TTL_USER_STORIES: TTL for user story data (10 minutes, hard-coded)
    """

    def __init__(self, client: TestIOClient, cache: InMemoryCache) -> None:
        """Initialize service with injected dependencies.

        Reads TTL values from settings for consistency with ADR-004.
        Services inherit these values and can override in tests if needed.

        Args:
            client: TestIO API client for making HTTP requests
            cache: In-memory cache for storing API responses
        """
        self.client = client
        self.cache = cache

        # Read TTL values from settings (STORY-007 AC3)
        self.CACHE_TTL_PRODUCTS = settings.CACHE_TTL_PRODUCTS
        self.CACHE_TTL_TESTS = settings.CACHE_TTL_TESTS
        self.CACHE_TTL_BUGS = settings.CACHE_TTL_BUGS
        # User stories TTL not in settings yet (future enhancement)
        self.CACHE_TTL_USER_STORIES = 600  # 10 minutes

        # Track in-flight fetches to prevent cache stampede (STORY-007 peer review fix)
        self._inflight_fetches: dict[str, asyncio.Task[dict[str, Any]]] = {}

    def _make_cache_key(self, *parts: str | int | None) -> str:
        """Create a consistent cache key from parts.

        Formats cache keys consistently across all services using colon-separated
        parts. Handles string, integer, and None parts (None converted to "None").

        Args:
            *parts: Variable number of parts to join (strings, integers, or None)

        Returns:
            Formatted cache key with parts joined by colons

        Example:
            >>> service._make_cache_key("test", 123, "status")
            'test:123:status'
            >>> service._make_cache_key("product", "list")
            'product:list'
            >>> service._make_cache_key("products", "list", None, None)
            'products:list:None:None'
        """
        return ":".join(str(part) for part in parts)

    async def _get_cached_or_fetch(
        self,
        cache_key: str,
        fetch_fn: Callable[[], Awaitable[dict[str, Any]]],
        ttl_seconds: int,
        transform_404: Exception | None = None,
    ) -> dict[str, Any]:
        """Get data from cache or fetch from API if not cached.

        Implements the cache-or-fetch pattern with stampede protection.
        When multiple concurrent requests miss the cache for the same key,
        only one fetch is executed while others wait for the result.

        Optionally transforms 404 errors into domain-specific exceptions.

        Args:
            cache_key: Cache key to check (use _make_cache_key to create)
            fetch_fn: Async function that fetches data from API
            ttl_seconds: Time-to-live for cached data in seconds
            transform_404: Optional exception instance to raise on 404 errors.
                If provided and API returns 404, raises this exception instead.

        Returns:
            Dictionary with API response data (from cache or fresh fetch)

        Raises:
            Exception: The exception provided in transform_404 if API returns 404
            TestIOAPIError: For non-404 API errors
            Exception: Any other errors from fetch_fn

        Example:
            >>> result = await self._get_cached_or_fetch(
            ...     cache_key=self._make_cache_key("test", test_id),
            ...     fetch_fn=lambda: self.client.get(f"tests/{test_id}"),
            ...     ttl_seconds=self.CACHE_TTL_TESTS,
            ...     transform_404=TestNotFoundException(test_id)
            ... )
        """
        # Check cache first (fast path)
        cached = await self.cache.get(cache_key)
        if cached is not None:
            # Cache returns Any, but we know it's dict[str, Any] from our usage
            from typing import cast

            return cast(dict[str, Any], cached)

        # Cache miss - check if fetch already in progress for this key
        inflight_task = self._inflight_fetches.get(cache_key)
        if inflight_task is not None:
            # Another coroutine is already fetching - wait for it
            try:
                result = await inflight_task
                return result
            except Exception:
                # If the in-flight fetch failed, we should retry ourselves
                # (the task will be cleaned up by the original fetcher)
                pass

        # No in-flight fetch - we need to fetch
        # Create task to coordinate with other concurrent requests
        async def fetch_and_cache() -> dict[str, Any]:
            """Fetch from API and cache result."""
            try:
                result = await fetch_fn()
            except TestIOAPIError as e:
                # Transform 404 errors if requested
                if e.status_code == 404 and transform_404 is not None:
                    raise transform_404 from e
                # Re-raise other API errors
                raise
            finally:
                # Always remove from in-flight tracking (success or failure)
                self._inflight_fetches.pop(cache_key, None)

            # Cache the result (only on success)
            await self.cache.set(cache_key, result, ttl_seconds=ttl_seconds)
            return result

        # Create and track the fetch task
        fetch_task = asyncio.create_task(fetch_and_cache())
        self._inflight_fetches[cache_key] = fetch_task

        # Execute the fetch
        return await fetch_task
