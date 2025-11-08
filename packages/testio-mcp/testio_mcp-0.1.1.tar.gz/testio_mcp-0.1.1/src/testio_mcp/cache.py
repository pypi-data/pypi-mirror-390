"""Simple in-memory cache with TTL support.

This module provides an async-only caching implementation with:
- TTL-based expiration (datetime-based for consistency)
- Thread-safe concurrent access (asyncio.Lock)
- Cache statistics tracking (hits/misses/hit rate)
- Manual cache management (delete, clear)

**CRITICAL WARNING: DO NOT create a synchronous wrapper for this cache.**

All interactions MUST be async to prevent event loop conflicts. Creating
a sync wrapper (e.g., using asyncio.get_event_loop().run_until_complete())
will cause "Event loop is closed" errors and other hard-to-debug issues.

**Always use:** await cache.get(...) / await cache.set(...)
**Never create:** SyncCacheWrapper or similar patterns

Reference: ADR-004 (Cache Strategy MVP)
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any


class InMemoryCache:
    """Simple in-memory cache with TTL support and statistics tracking.

    ASYNC ONLY - all methods are async. Services must use 'await cache.get()'.

    Features:
    - TTL-based expiration with automatic cleanup on access
    - Thread-safe concurrent access via asyncio.Lock
    - Hit/miss statistics tracking for monitoring
    - Manual cache entry deletion and full cache clearing

    Expiration Strategy:
    - Lazy expiration: Expired entries removed on get() access
    - No background cleanup task (keeps implementation simple)
    - Uses datetime.now(UTC) for consistent timezone handling

    Example:
        >>> cache = InMemoryCache()
        >>> await cache.set("test:123:status", data, ttl_seconds=300)
        >>> value = await cache.get("test:123:status")
        >>> stats = await cache.get_stats()
        >>> print(f"Hit rate: {stats['hit_rate_percent']}%")

    Attributes:
        _cache: Dictionary mapping cache keys to (value, expiration_time) tuples
        _lock: Asyncio lock for thread-safe concurrent access
        _hits: Counter for cache hits (value found and not expired)
        _misses: Counter for cache misses (value not found or expired)
    """

    def __init__(self) -> None:
        """Initialize empty cache with statistics tracking."""
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Any | None:
        """Get value from cache if exists and not expired.

        Automatically removes expired entries during access. Updates hit/miss
        statistics for monitoring.

        Args:
            key: Cache key (e.g., "test:12345:status")

        Returns:
            Cached value if found and not expired, None otherwise

        Example:
            >>> cached = await cache.get("test:12345:status")
            >>> if cached:
            ...     print("Cache hit!")
            ... else:
            ...     print("Cache miss - fetch from API")
        """
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expires_at = self._cache[key]

            # Check expiration
            if datetime.now(UTC) > expires_at:
                # Expired - remove from cache
                del self._cache[key]
                self._misses += 1
                return None

            self._hits += 1
            return value

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key (e.g., "test:12345:status")
            value: Value to cache (any JSON-serializable type)
            ttl_seconds: Time-to-live in seconds (e.g., 300 for 5 minutes)

        Example:
            >>> await cache.set("test:12345:status", {"status": "running"}, ttl_seconds=300)
        """
        async with self._lock:
            expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
            self._cache[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        """Remove value from cache.

        Safe to call even if key doesn't exist (no-op).

        Args:
            key: Cache key to remove

        Example:
            >>> await cache.delete("test:12345:status")
        """
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        """Clear all cache entries and reset statistics.

        Removes all cached data and resets hit/miss counters to zero.
        Useful for testing or forcing fresh API queries.

        Example:
            >>> await cache.clear()
            >>> stats = await cache.get_stats()
            >>> assert stats["cached_keys"] == 0
            >>> assert stats["hits"] == 0
        """
        async with self._lock:
            self._cache.clear()
            # Reset statistics
            self._hits = 0
            self._misses = 0

    async def get_stats(self) -> dict[str, Any]:
        """Get cache performance statistics.

        Returns hit rate, total requests, and current cache size for monitoring
        cache effectiveness.

        Returns:
            Dictionary with statistics:
            - hits: Number of successful cache hits
            - misses: Number of cache misses (not found or expired)
            - total_requests: Total get() calls (hits + misses)
            - hit_rate_percent: Percentage of requests served from cache
            - cached_keys: Current number of entries in cache

        Example:
            >>> stats = await cache.get_stats()
            >>> print(f"Hit rate: {stats['hit_rate_percent']}%")
            >>> print(f"Total requests: {stats['total_requests']}")
            87.5
            120
        """
        async with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total,
                "hit_rate_percent": round(hit_rate, 2),
                "cached_keys": len(self._cache),
            }
