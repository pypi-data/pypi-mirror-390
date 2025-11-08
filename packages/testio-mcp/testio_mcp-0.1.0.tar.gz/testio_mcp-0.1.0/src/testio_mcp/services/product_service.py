"""Product service for product listing and discovery operations.

This service handles business logic for product queries, following
the service layer pattern (ADR-006). It is framework-agnostic and can
be used from MCP tools, REST APIs, CLI, or webhooks.

Responsibilities:
- Cache management (check/store with TTL)
- API call orchestration
- Data filtering (search, product_type)
- Domain exception raising

Does NOT handle:
- MCP protocol formatting
- User-facing error messages
- HTTP transport concerns
"""

import asyncio
import logging
from enum import Enum
from typing import Any

from testio_mcp.exceptions import ProductNotFoundException
from testio_mcp.services.base_service import BaseService

logger = logging.getLogger(__name__)

# Valid test statuses from TestIO Customer API (AC1)
VALID_STATUSES = [
    "running",
    "locked",
    "archived",
    "cancelled",
    "customer_finalized",
    "initialized",
]


def _extract_enum_value(value: str | Enum) -> str:
    """Extract string value from enum or return string as-is.

    Helper for accepting both enum instances (from MCP tools) and raw strings
    (from tests, future REST API, etc.) without requiring conversion at call sites.

    Args:
        value: String or enum instance

    Returns:
        String value

    Example:
        >>> _extract_enum_value(TestStatus.RUNNING)
        'running'
        >>> _extract_enum_value("running")
        'running'
    """
    return value.value if isinstance(value, Enum) else value


class ProductService(BaseService):
    """Business logic for product operations.

    Inherits from BaseService to get standard dependency injection and
    cache helper methods.

    Example:
        ```python
        service = ProductService(client=client, cache=cache)
        products = await service.list_products(search="studio")
        ```
    """

    async def list_products(
        self,
        search: str | None = None,
        product_type: str | None = None,
    ) -> dict[str, Any]:
        """List all products accessible to the user with optional filtering.

        Implements cache-raw pattern (ADR-004):
        1. Cache full API response (no filter in cache key)
        2. Filter in-memory on every call (fast, <1ms)
        3. Result: 95%+ cache hit rate regardless of filter combinations

        Args:
            search: Optional search term (filters by name/description)
            product_type: Optional filter by product type

        Returns:
            Dictionary with product list and metadata

        Raises:
            TestIOAPIError: If API returns error response

        Example:
            >>> products = await service.list_products(search="studio")
            >>> print(products["total_count"])
            2
            >>> print(products["products"][0]["name"])
            'Studio Pro'
        """

        # Cache-raw pattern: cache key WITHOUT filters (cache full API response)
        cache_key = self._make_cache_key("products", "list", "raw")

        # Fetch raw products (cached or fresh)
        async def fetch_raw() -> dict[str, Any]:
            """Fetch raw products from API (no filtering)."""
            return await self.client.get("products")

        raw_response = await self._get_cached_or_fetch(
            cache_key=cache_key,
            fetch_fn=fetch_raw,
            ttl_seconds=self.CACHE_TTL_PRODUCTS,
        )

        # Always filter in-memory (fast, <1ms)
        all_products = raw_response.get("products", [])
        filtered_products = self._apply_filters(all_products, search, product_type)

        # Build result with filter metadata
        return {
            "total_count": len(filtered_products),
            "filters_applied": {
                "search": search,
                "product_type": product_type,
            },
            "products": filtered_products,
        }

    def _apply_filters(
        self,
        products: list[dict[str, Any]],
        search: str | None,
        product_type: str | None,
    ) -> list[dict[str, Any]]:
        """Apply search and type filters to products.

        This is a private helper method that filters raw product data:
        - Search: Case-insensitive substring match on name or description
        - Product type: Exact match on type field

        Args:
            products: List of product dictionaries from API
            search: Optional search term
            product_type: Optional product type filter

        Returns:
            Filtered list of products

        Example:
            >>> products = [
            ...     {"id": "1", "name": "Studio Pro", "type": "website"},
            ...     {"id": "2", "name": "Mobile App", "type": "mobile"}
            ... ]
            >>> filtered = service._apply_filters(products, "studio", None)
            >>> len(filtered)
            1
            >>> filtered[0]["name"]
            'Studio Pro'
        """
        filtered = products

        # Filter by search term (case-insensitive, name or description)
        if search:
            search_lower = search.lower()
            filtered = [
                p
                for p in filtered
                if search_lower in (p.get("name") or "").lower()
                or search_lower in (p.get("description") or "").lower()
            ]

        # Filter by product type
        if product_type:
            filtered = [p for p in filtered if p.get("type") == product_type]

        return filtered

    def _validate_statuses(self, statuses: list[str]) -> None:
        """Validate that all provided statuses are valid.

        Args:
            statuses: List of status strings to validate

        Raises:
            ValueError: If any status is invalid with descriptive message
                       listing all valid statuses

        Example:
            >>> service._validate_statuses(["running", "locked"])  # No error
            >>> service._validate_statuses(["invalid"])  # Raises ValueError
        """
        invalid = [s for s in statuses if s not in VALID_STATUSES]
        if invalid:
            raise ValueError(
                f"Invalid status values: {', '.join(invalid)}. "
                f"Valid statuses: {', '.join(VALID_STATUSES)}"
            )

    async def list_tests(
        self,
        product_id: int,
        statuses: list[str | Enum] | None = None,
        include_bug_counts: bool = False,
    ) -> dict[str, Any]:
        """List tests for a specific product with flexible status filtering.

        This method:
        1. Extracts enum values if enums provided (STORY-018 AC4)
        2. Validates statuses if provided (runtime validation)
        3. Checks cache for cached response
        4. If cache miss, fetches product details and tests in parallel
        5. Applies status filtering (None or [] means return all tests)
        6. Optionally fetches and aggregates bug counts per test
        7. Caches the result with 5 minute TTL
        8. Returns structured data with effective statuses

        Args:
            product_id: The product ID (integer from API, e.g., 25073)
            statuses: Filter by test statuses (enums or strings).
                     Default: None (returns ALL tests)
                     Available: running, locked, archived, cancelled,
                                customer_finalized, initialized
                     None or [] means return all tests (no filtering)
            include_bug_counts: Include bug count summary for each test. Default: False

        Returns:
            Dictionary with product info, filtered tests, and optional bug counts:
            - product: Product details
            - tests: Filtered test list
            - statuses_filter: Effective statuses used (all 6 if None/[], exact list otherwise)
            - bug_counts: Optional bug aggregations

        Raises:
            ValueError: If any status value is invalid
            ProductNotFoundException: If product ID doesn't exist (404)
            TestIOAPIError: If API returns error response

        Example:
            >>> result = await service.list_tests(product_id=25073)
            >>> print(result["statuses_filter"])  # All 6 valid statuses
            ['running', 'locked', 'archived', 'cancelled', 'customer_finalized', 'initialized']
            >>> result = await service.list_tests(product_id=25073, statuses=["running"])
            >>> print(result["statuses_filter"])
            ['running']
        """
        # Extract enum values if needed (STORY-018 AC4 - supports both enums and strings)
        statuses_str: list[str] | None = (
            [_extract_enum_value(s) for s in statuses] if statuses is not None else None
        )

        # Validate statuses if provided (AC6 - runtime validation)
        if statuses_str is not None and len(statuses_str) > 0:
            self._validate_statuses(statuses_str)

        # Determine effective statuses for response (AC8 - output contract)
        effective_statuses = statuses_str if statuses_str else VALID_STATUSES

        # Cache-raw pattern (ADR-004, ADR-014): cache key WITHOUT filters
        cache_key = self._make_cache_key("product", product_id, "tests", "raw")

        # Fetch raw data (product + tests) - cached or fresh
        async def fetch_raw() -> dict[str, Any]:
            """Fetch raw product and tests from API (no filtering)."""
            product_data, tests_data = await asyncio.gather(
                self.client.get(f"products/{product_id}"),
                self.client.get(f"products/{product_id}/exploratory_tests"),
            )
            return {
                "product": product_data.get("product", {}),
                "tests": tests_data.get("exploratory_tests", []),
            }

        raw_response = await self._get_cached_or_fetch(
            cache_key=cache_key,
            fetch_fn=fetch_raw,
            ttl_seconds=self.CACHE_TTL_TESTS,
            transform_404=ProductNotFoundException(product_id),
        )

        # Always filter in-memory (fast, <1ms) - after cache retrieval
        all_tests = raw_response["tests"]
        if statuses_str is None or len(statuses_str) == 0:
            filtered_tests = all_tests  # No filtering - return all
        else:
            filtered_tests = [t for t in all_tests if t.get("status") in statuses_str]

        # Optionally fetch bug counts (NOT cached - separate concern)
        bug_counts: dict[str, dict[str, Any]] = {}
        if include_bug_counts:
            try:
                bugs_data = await self.client.get(f"bugs?filter_product_ids={product_id}")
                bug_counts = self._aggregate_bug_counts(bugs_data.get("bugs", []))
            except Exception as e:
                # Log warning but don't fail - bugs are optional
                logger.warning(f"Failed to fetch bug counts for product {product_id}: {e}")

        # Build response with effective statuses (AC8 - output contract clarity)
        return {
            "product": raw_response["product"],
            "tests": filtered_tests,
            "statuses_filter": effective_statuses,  # Shows what filter was applied
            "bug_counts": bug_counts,
        }

    def _filter_by_statuses(
        self, tests: list[dict[str, Any]], statuses: list[str]
    ) -> list[dict[str, Any]]:
        """Filter tests by list of statuses.

        Args:
            tests: List of test dictionaries from API
            statuses: List of status strings to filter by

        Returns:
            Filtered list of tests

        Example:
            >>> tests = [
            ...     {"id": "1", "status": "running"},
            ...     {"id": "2", "status": "archived"}
            ... ]
            >>> filtered = service._filter_by_statuses(tests, ["running"])
            >>> len(filtered)
            1
        """
        if not statuses:  # Empty list means return all
            return tests
        return [t for t in tests if t.get("status") in statuses]

    def _aggregate_bug_counts(self, bugs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Aggregate bugs by test_cycle_id.

        Groups bugs by test ID and counts them by severity.

        Args:
            bugs: List of bug dictionaries from API

        Returns:
            Dictionary mapping test_id -> {total: int, by_severity: {severity: count}}

        Example:
            >>> bugs = [
            ...     {"test": {"id": "1"}, "severity": "high"},
            ...     {"test": {"id": "1"}, "severity": "low"}
            ... ]
            >>> counts = service._aggregate_bug_counts(bugs)
            >>> counts["1"]["total"]
            2
            >>> counts["1"]["by_severity"]["high"]
            1
        """
        bug_counts: dict[str, dict[str, Any]] = {}
        for bug in bugs:
            test_id = str(bug.get("test", {}).get("id", ""))
            if not test_id:
                continue

            if test_id not in bug_counts:
                bug_counts[test_id] = {"total": 0, "by_severity": {}}

            bug_counts[test_id]["total"] += 1
            severity = bug.get("severity", "unknown")
            bug_counts[test_id]["by_severity"][severity] = (
                bug_counts[test_id]["by_severity"].get(severity, 0) + 1
            )

        return bug_counts
