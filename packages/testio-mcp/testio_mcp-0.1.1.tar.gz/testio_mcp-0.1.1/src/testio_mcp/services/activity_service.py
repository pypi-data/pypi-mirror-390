"""Activity service for timeframe-based test activity analysis.

This service handles business logic for analyzing test activity across
products within date ranges, following the service layer pattern (ADR-006).
It is framework-agnostic and can be used from MCP tools, REST APIs, CLI, or webhooks.

Responsibilities:
- Date range filtering logic
- Product-wise activity aggregation
- Testing type distribution calculation
- Timeline data generation for visualization
- Cache integration for product names

Does NOT handle:
- MCP protocol formatting
- User-facing error messages
- HTTP transport concerns
"""

import asyncio
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from testio_mcp.exceptions import TestIOAPIError
from testio_mcp.services.base_service import BaseService


def _extract_enum_value(value: str | Enum) -> str:
    """Extract string value from enum or return string as-is (STORY-018 AC4)."""
    return value.value if isinstance(value, Enum) else value


class ActivityService(BaseService):
    """Business logic for timeframe-based activity analysis across products.

    Inherits from BaseService to get standard dependency injection and
    cache helper methods.

    Example:
        ```python
        service = ActivityService(client=client, cache=cache)
        activity = await service.get_activity_by_timeframe(
            product_ids=["25073"],
            start_date="2024-10-01",
            end_date="2024-12-31"
        )
        ```
    """

    async def get_activity_by_timeframe(
        self,
        product_ids: list[int],
        start_date: str,
        end_date: str,
        date_field: str | Enum = "start_at",
        include_bugs: bool = False,
    ) -> dict[str, Any]:
        """Get test activity across products within a date range.

        This method:
        1. Extracts enum value if enum provided (STORY-018 AC4)
        2. Validates product count (max 100) and date range (max 365 days)
        3. Parses and validates dates
        4. Fetches tests for all products concurrently
        5. Filters tests by specified date_field parameter
        6. Aggregates activity metrics per product
        7. Calculates testing type distribution
        8. Generates timeline data for visualization
        9. Optionally includes bug metrics

        Args:
            product_ids: List of product IDs (1-100 products)
            start_date: Start date in YYYY-MM-DD format (e.g., "2024-10-01")
            end_date: End date in YYYY-MM-DD format (e.g., "2024-12-31")
            date_field: Date to filter by (enum or string):
                "created_at", "start_at" (default), "end_at", "any"
            include_bugs: Include bug count metrics (default: False)

        Returns:
            Dictionary with activity summary, product breakdown, and timeline data

        Raises:
            ValueError: If date range invalid, too many products, or invalid date_field
            ProductNotFoundException: If product not found (404)
            TestIOAPIError: For other API errors

        Example:
            >>> activity = await service.get_activity_by_timeframe(
            ...     product_ids=["25073"],
            ...     start_date="2024-10-01",
            ...     end_date="2024-12-31",
            ...     date_field="start_at"
            ... )
            >>> print(activity["total_tests"])
            5
        """
        # Extract enum value if needed (STORY-018 AC4 - supports both enums and strings)
        date_field_str = _extract_enum_value(date_field)

        # Validate inputs
        self._validate_inputs(product_ids, start_date, end_date, date_field_str)

        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC)
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=UTC)

        # Fetch tests for all products concurrently
        failed_products: list[str] = []
        all_tests_by_product = await self._fetch_product_tests(product_ids, failed_products)

        # Build product activity summaries
        product_activities = []
        all_filtered_tests = []

        for product_id, tests in all_tests_by_product.items():
            # Filter tests by timeframe
            filtered_tests = self._filter_tests_by_timeframe(
                tests, start_dt, end_dt, date_field_str
            )
            all_filtered_tests.extend(filtered_tests)

            # Get product name (cached)
            product_name = await self._get_product_name(product_id)

            # Calculate testing type distribution
            testing_types = self._calculate_testing_type_distribution(filtered_tests)

            # Build activity summary
            product_activities.append(
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "tests_created": len(
                        [
                            t
                            for t in filtered_tests
                            if self._date_in_range(t.get("created_at"), start_dt, end_dt)
                        ]
                    ),
                    "tests_started": len(
                        [
                            t
                            for t in filtered_tests
                            if self._date_in_range(t.get("start_at"), start_dt, end_dt)
                        ]
                    ),
                    "tests_completed": len(
                        [
                            t
                            for t in filtered_tests
                            if self._date_in_range(t.get("end_at"), start_dt, end_dt)
                        ]
                    ),
                    "total_tests_in_range": len(filtered_tests),
                    "testing_types": testing_types,
                    "tests": [
                        {
                            "id": t.get("id"),
                            "title": t.get("title") or t.get("test_title") or "Untitled",
                            "status": t.get("status") or "unknown",
                            "testing_type": t.get("testing_type") or "other",
                        }
                        for t in filtered_tests
                    ],
                }
            )

        # Calculate overall metrics
        overall_testing_types = self._calculate_testing_type_distribution(all_filtered_tests)
        timeline_data = self._generate_timeline_data(
            all_filtered_tests, start_dt, end_dt, date_field_str
        )

        # Build result
        result: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
            "days_in_range": (end_dt - start_dt).days + 1,
            "total_products": len(product_ids),
            "total_tests": len(all_filtered_tests),
            "overall_testing_types": overall_testing_types,
            "products": product_activities,
            "timeline_data": timeline_data,
            "failed_products": failed_products,
        }

        # Optional bug metrics
        if include_bugs:
            await self._add_bug_metrics(product_activities, product_ids, start_dt, end_dt)

        return result

    def _validate_inputs(
        self,
        product_ids: list[int],
        start_date: str,
        end_date: str,
        date_field: str,
    ) -> None:
        """Validate input parameters.

        Args:
            product_ids: List of product IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            date_field: Date field to filter by

        Raises:
            ValueError: If validation fails
        """
        # Validate product count (max 100 per ADR-005)
        if not product_ids:
            raise ValueError("❌ product_ids cannot be empty\n💡 Provide at least one product ID")

        if len(product_ids) > 100:
            raise ValueError(
                f"❌ Query includes {len(product_ids)} products but maximum is 100\n"
                f"ℹ️  Large queries can cause slow responses and timeout\n"
                f"💡 Reduce number of products or split into multiple queries\n"
                f"   Example: First 100, then next batch"
            )

        # Validate date format
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"❌ Invalid date format: {e}\n💡 Use YYYY-MM-DD format (e.g., '2024-10-01')"
            ) from e

        # Validate date range
        if end_dt < start_dt:
            raise ValueError(f"❌ end_date ({end_date}) must be after start_date ({start_date})")

        # Validate date range limit (max 365 days per ADR-005)
        # Note: (end - start).days gives the difference in days, but inclusive counting
        # means we need to add 1. So 2024-01-01 to 2024-01-02 is 1 day diff but 2 days inclusive.
        # Maximum allowed is 365 days inclusive.
        days_diff = (end_dt - start_dt).days
        days_inclusive = days_diff + 1
        if days_inclusive > 365:
            raise ValueError(
                f"❌ Date range {days_inclusive} days (inclusive) exceeds maximum 365 days\n"
                f"ℹ️  Very large date ranges cause slow queries and may timeout\n"
                f"💡 Reduce date range to 1 year or less for better performance"
            )

        # Validate date_field
        allowed_fields = ["created_at", "start_at", "end_at", "any"]
        if date_field not in allowed_fields:
            raise ValueError(
                f"❌ Invalid date_field: '{date_field}'\n"
                f"💡 Must be one of: {', '.join(allowed_fields)}"
            )

    async def _fetch_product_tests(
        self, product_ids: list[int], failed_products: list[str]
    ) -> dict[str, list[dict[str, Any]]]:
        """Fetch tests for all products concurrently with timeout protection.

        Args:
            product_ids: List of product IDs
            failed_products: List to populate with failed product IDs (modified in-place)

        Returns:
            Dictionary mapping product_id to list of tests

        Raises:
            TimeoutError: If query takes longer than 60 seconds (STORY-008 AC8)

        Note:
            Uses return_exceptions=True to handle partial failures gracefully.
            Failed products (TestIOAPIError) get empty list and are recorded in failed_products.
            Other exceptions (timeouts, etc.) are re-raised for proper error handling.
        """
        # STORY-008 AC8: Add timeout protection for complex queries
        try:
            results = await asyncio.wait_for(
                asyncio.gather(
                    *[self.client.get(f"products/{pid}/exploratory_tests") for pid in product_ids],
                    return_exceptions=True,
                ),
                timeout=60.0,  # 60 second total timeout for all product fetches
            )
        except TimeoutError as e:
            raise ValueError(
                f"⏱️  Query timed out after 60 seconds\n"
                f"ℹ️  Your query across {len(product_ids)} products was too complex\n"
                f"💡 Try reducing the number of products or narrowing the date range"
            ) from e

        all_tests_by_product: dict[str, list[dict[str, Any]]] = {}
        for idx, result in enumerate(results):
            product_id = product_ids[idx]
            product_id_str = str(product_id)
            if isinstance(result, TestIOAPIError):
                # API error (404, 403, etc.) - record failure and continue
                failed_products.append(product_id_str)
                all_tests_by_product[product_id_str] = []
            elif isinstance(result, Exception):
                # Unexpected error (timeout, network, etc.) - re-raise
                raise result
            elif isinstance(result, dict):
                all_tests_by_product[product_id_str] = result.get("exploratory_tests", [])

        return all_tests_by_product

    def _filter_tests_by_timeframe(
        self,
        tests: list[dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
        date_field: str = "start_at",
    ) -> list[dict[str, Any]]:
        """Filter tests based on specified date field.

        Args:
            tests: List of test dictionaries
            start_date: Start of date range
            end_date: End of date range
            date_field: Which date to check

        Returns:
            Filtered list of tests
        """
        filtered = []
        for test in tests:
            if self._is_test_in_timeframe(test, start_date, end_date, date_field):
                filtered.append(test)
        return filtered

    def _is_test_in_timeframe(
        self,
        test: dict[str, Any],
        start_date: datetime,
        end_date: datetime,
        date_field: str = "start_at",
    ) -> bool:
        """Check if test falls within timeframe based on specified date field.

        Args:
            test: Test dictionary
            start_date: Start of date range
            end_date: End of date range
            date_field: Which date to check - "created_at", "start_at", "end_at", or "any"

        Returns:
            True if test matches date criteria
        """
        if date_field == "any":
            # Include if ANY date falls in range (most inclusive)
            for field in ["created_at", "start_at", "end_at"]:
                if self._date_in_range(test.get(field), start_date, end_date):
                    return True
            return False
        else:
            # Filter by specific field (created_at, start_at, or end_at)
            return self._date_in_range(test.get(date_field), start_date, end_date)

    def _date_in_range(
        self, date_str: str | None, start_date: datetime, end_date: datetime
    ) -> bool:
        """Check if ISO date string falls within range.

        Args:
            date_str: ISO 8601 date string (e.g., "2024-10-15T10:30:00Z")
            start_date: Start of date range
            end_date: End of date range

        Returns:
            True if date is within range, False otherwise
        """
        if not date_str:
            return False
        try:
            test_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return start_date <= test_date <= end_date
        except (ValueError, AttributeError):
            return False

    def _calculate_testing_type_distribution(self, tests: list[dict[str, Any]]) -> dict[str, int]:
        """Calculate distribution of testing types.

        Args:
            tests: List of test dictionaries

        Returns:
            Dictionary mapping testing type to count
        """
        distribution = {
            "rapid": 0,
            "focused": 0,
            "coverage": 0,
            "usability": 0,
            "other": 0,
        }

        for test in tests:
            testing_type = test.get("testing_type", "other")
            if testing_type in distribution:
                distribution[testing_type] += 1
            else:
                distribution["other"] += 1

        return distribution

    def _generate_timeline_data(
        self,
        tests: list[dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
        date_field: str = "start_at",
    ) -> dict[str, int]:
        """Generate timeline data for visualization.

        Groups tests by week (if range <= 60 days) or month (if range > 60 days).

        Args:
            tests: List of test dictionaries
            start_date: Start of date range
            end_date: End of date range
            date_field: Which date field to use for bucketing (created_at, start_at, end_at, any)

        Returns:
            Dictionary mapping time bucket to count

        Note:
            If date_field is "any", uses the first available date (created_at, start_at, end_at).
            This ensures timeline buckets align with the selected filtering criteria.
        """
        delta_days = (end_date - start_date).days
        timeline: dict[str, int] = {}

        for test in tests:
            # Determine which date to use for bucketing based on date_field
            if date_field == "any":
                # Use first available date
                test_date = (
                    self._parse_iso_date(test.get("created_at"))
                    or self._parse_iso_date(test.get("start_at"))
                    or self._parse_iso_date(test.get("end_at"))
                )
            else:
                # Use specified field
                test_date = self._parse_iso_date(test.get(date_field))

            if not test_date:
                continue

            # Determine bucket label
            if delta_days <= 60:
                # Weekly buckets: "2024-W42" format
                year, week, _ = test_date.isocalendar()
                bucket = f"{year}-W{week:02d}"
            else:
                # Monthly buckets: "2024-10" format
                bucket = test_date.strftime("%Y-%m")

            timeline[bucket] = timeline.get(bucket, 0) + 1

        # Sort chronologically
        return dict(sorted(timeline.items()))

    def _parse_iso_date(self, date_str: str | None) -> datetime | None:
        """Parse ISO 8601 datetime string to datetime object.

        Args:
            date_str: ISO 8601 date string

        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not date_str:
            return None
        try:
            # Parse ISO format (e.g., "2024-10-15T10:30:00Z")
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    async def _get_product_name(self, product_id: str) -> str:
        """Get product name with caching.

        Args:
            product_id: Product ID

        Returns:
            Product name or fallback string
        """
        # Check cache first using BaseService helper
        cache_key = self._make_cache_key("product", product_id, "name")
        cached_name = await self.cache.get(cache_key)
        if cached_name:
            return str(cached_name)

        # Cache miss - fetch from API
        try:
            product_data = await self.client.get(f"products/{product_id}")
            product_name = str(product_data.get("name", f"Product {product_id}"))
            await self.cache.set(cache_key, product_name, ttl_seconds=self.CACHE_TTL_PRODUCTS)
            return product_name
        except TestIOAPIError:
            # Return fallback if product fetch fails
            return f"Product {product_id}"

    async def _add_bug_metrics(
        self,
        product_activities: list[dict[str, Any]],
        product_ids: list[int],
        start: datetime,
        end: datetime,
    ) -> None:
        """Add bug count metrics to product activities.

        Args:
            product_activities: List of product activity dictionaries (modified in-place)
            product_ids: List of product IDs
            start: Start of date range
            end: End of date range
        """
        bugs_results = await asyncio.gather(
            *[self.client.get(f"bugs?filter_product_ids={pid}") for pid in product_ids],
            return_exceptions=True,
        )

        bugs_by_product: dict[str, int] = {}
        for idx, result in enumerate(bugs_results):
            product_id = product_ids[idx]
            product_id_str = str(product_id)
            if isinstance(result, TestIOAPIError):
                # API error - skip this product's bug count (will be 0)
                continue
            elif isinstance(result, Exception):
                # Unexpected error - re-raise
                raise result
            elif isinstance(result, dict):
                bugs = result.get("bugs", [])
                bugs_in_range = [
                    b for b in bugs if self._date_in_range(b.get("created_at"), start, end)
                ]
                bugs_by_product[product_id_str] = len(bugs_in_range)

        # Update product activities with bug counts
        for activity in product_activities:
            activity["bug_count"] = bugs_by_product.get(activity["product_id"], 0)
