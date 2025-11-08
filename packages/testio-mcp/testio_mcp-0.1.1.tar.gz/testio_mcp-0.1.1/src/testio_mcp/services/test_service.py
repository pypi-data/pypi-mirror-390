"""Test service for exploratory test status operations.

This service handles business logic for test status queries, following
the service layer pattern (ADR-006). It is framework-agnostic and can
be used from MCP tools, REST APIs, CLI, or webhooks.

Responsibilities:
- Cache management (check/store with TTL)
- API call orchestration (parallel fetches)
- Data aggregation (test + bugs)
- Domain exception raising

Does NOT handle:
- MCP protocol formatting
- User-facing error messages
- HTTP transport concerns
"""

import asyncio
from typing import Any

from testio_mcp.exceptions import TestNotFoundException
from testio_mcp.services.base_service import BaseService


class TestService(BaseService):
    """Business logic for exploratory test operations.

    Inherits from BaseService to get standard dependency injection and
    cache helper methods.

    Example:
        ```python
        service = TestService(client=client, cache=cache)
        status = await service.get_test_status(test_id=109363)
        ```
    """

    __test__ = False

    async def get_test_status(self, test_id: int) -> dict[str, Any]:
        """Get comprehensive status of a single exploratory test.

        This method:
        1. Checks cache for cached response
        2. If cache miss, fetches test details and bugs concurrently
        3. Aggregates bug summary statistics
        4. Caches the result with 5 minute TTL
        5. Returns structured data

        Args:
            test_id: Exploratory test ID (integer from API, e.g., 109363)

        Returns:
            Dictionary with complete test details and bug summary

        Raises:
            TestNotFoundException: If test ID not found (404)
            TestIOAPIError: If API returns error response

        Example:
            >>> status = await service.get_test_status(109363)
            >>> print(status["test"]["title"])
            'Evgeniya Testing'
            >>> print(status["bugs"]["total_count"])
            1
        """

        async def fetch_and_aggregate() -> dict[str, Any]:
            """Fetch test data and bugs, then aggregate into response."""
            # Fetch from API concurrently
            test_data, bugs_data = await asyncio.gather(
                self.client.get(f"exploratory_tests/{test_id}"),
                self.client.get(f"bugs?filter_test_cycle_ids={test_id}"),
            )

            # Extract data from responses
            test = test_data.get("exploratory_test", {})
            bugs = bugs_data.get("bugs", [])

            # Aggregate bug summary
            bug_summary = self._aggregate_bug_summary(bugs)

            # Build response (keep IDs as integers from API)
            return {
                "test": {
                    "id": test["id"],
                    "title": test["title"],
                    "goal": test.get("goal"),
                    "testing_type": test["testing_type"],
                    "duration": test.get("duration"),
                    "status": test["status"],
                    "review_status": test.get("review_status"),
                    "requirements": test.get("requirements"),
                    "created_at": test.get("created_at"),
                    "starts_at": test.get("starts_at"),
                    "ends_at": test.get("ends_at"),
                    "product": {
                        "id": test["product"]["id"],
                        "name": test["product"]["name"],
                    },
                    "feature": (
                        {
                            "id": test["feature"]["id"],
                            "name": test["feature"]["name"],
                        }
                        if test.get("feature")
                        else None
                    ),
                },
                "bugs": bug_summary,
            }

        # Use BaseService helper for cache-or-fetch pattern with 404 transformation
        return await self._get_cached_or_fetch(
            cache_key=self._make_cache_key("test", test_id, "status"),
            fetch_fn=fetch_and_aggregate,
            ttl_seconds=self.CACHE_TTL_TESTS,
            transform_404=TestNotFoundException(test_id),
        )

    def _aggregate_bug_summary(self, bugs: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate bug data into summary statistics.

        This is a private helper method that processes raw bug data from
        the API into a structured summary with:
        - Total count
        - Counts by severity
        - Counts by status (active_accepted, auto_accepted, rejected, open)
        - Acceptance rates (if auto_accepted field available)
        - Recent bugs (last 3)

        Bug Status Taxonomy (STORY-005c):
        - active_accepted: status="accepted" AND auto_accepted=false
        - auto_accepted: status="accepted" AND auto_accepted=true
        - total_accepted: active_accepted + auto_accepted (derived)
        - rejected: status="rejected"
        - open: status="forwarded" (awaiting customer triage)

        Args:
            bugs: List of bug dictionaries from API

        Returns:
            Dictionary with aggregated bug statistics

        Example:
            >>> bugs = [
            ...     {"id": 1, "severity": "high", "status": "accepted", "auto_accepted": false},
            ...     {"id": 2, "severity": "low", "status": "forwarded"}
            ... ]
            >>> summary = service._aggregate_bug_summary(bugs)
            >>> summary["total_count"]
            2
            >>> summary["by_severity"]["high"]
            1
            >>> summary["by_status"]["active_accepted"]
            1
            >>> summary["by_status"]["open"]
            1
        """
        summary: dict[str, Any] = {
            "total_count": len(bugs),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "low": 0,
                "visual": 0,
                "content": 0,
                "custom": 0,
            },
            "by_status": {
                "active_accepted": 0,
                "auto_accepted": 0,
                "total_accepted": 0,
                "rejected": 0,
                "open": 0,
            },
            "acceptance_rates": None,
            "recent_bugs": [],
        }

        # Track if any bug has auto_accepted field (production vs staging)
        # Check ALL bugs, not just accepted ones, to detect production API support
        has_auto_accepted_field = False

        for bug in bugs:
            # Count by severity
            severity = bug.get("severity", "unknown")
            if severity in summary["by_severity"]:
                summary["by_severity"][severity] += 1

            # Count by status with auto-acceptance classification
            status = bug.get("status", "unknown")
            auto_accepted = bug.get("auto_accepted")

            # Detect production API support by checking for auto_accepted field on ANY bug
            # This ensures we calculate acceptance rates even for rejection-only tests
            if auto_accepted is not None:
                has_auto_accepted_field = True

            if status == "accepted":
                # Distinguish active vs auto acceptance (STORY-005c AC1)
                if auto_accepted is None:
                    # Staging: field missing, use conservative default (count as active)
                    summary["by_status"]["active_accepted"] += 1
                elif auto_accepted:
                    # Production: auto-accepted after 10 days
                    summary["by_status"]["auto_accepted"] += 1
                else:
                    # Production: actively accepted by customer
                    summary["by_status"]["active_accepted"] += 1
            elif status == "rejected":
                summary["by_status"]["rejected"] += 1
            elif status == "forwarded":
                # Map API "forwarded" to user-facing "open" (STORY-005c Decision 6)
                summary["by_status"]["open"] += 1

        # Calculate total_accepted (derived field)
        summary["by_status"]["total_accepted"] = (
            summary["by_status"]["active_accepted"] + summary["by_status"]["auto_accepted"]
        )

        # Calculate acceptance rates if auto_accepted field available (STORY-005c AC2)
        if has_auto_accepted_field:
            summary["acceptance_rates"] = self._calculate_acceptance_rates(summary["by_status"])

        # Get 3 most recent bugs (sorted by created_at descending)
        sorted_bugs = sorted(
            bugs,
            key=lambda b: b.get("created_at", ""),
            reverse=True,
        )
        summary["recent_bugs"] = [
            {
                "id": str(bug["id"]),
                "title": bug["title"],
                "severity": bug["severity"],
                "status": bug["status"],
                "created_at": bug.get("created_at"),
            }
            for bug in sorted_bugs[:3]
        ]

        return summary

    def _calculate_acceptance_rates(self, bugs_by_status: dict[str, int]) -> dict[str, Any] | None:
        """Calculate acceptance rates from triaged bugs.

        Acceptance rates are calculated from triaged bugs only (bugs that have
        been reviewed by the customer). Open (forwarded) bugs are excluded.

        Triaged bugs = active_accepted + auto_accepted + rejected

        Args:
            bugs_by_status: Dictionary with bug counts by status

        Returns:
            Dictionary with acceptance rates or None if no triaged bugs

        Example:
            >>> bugs_by_status = {
            ...     "active_accepted": 12,
            ...     "auto_accepted": 3,
            ...     "rejected": 3,
            ...     "open": 5
            ... }
            >>> rates = service._calculate_acceptance_rates(bugs_by_status)
            >>> rates["active_acceptance_rate"]
            0.6666666666666666
            >>> rates["triaged_count"]
            18
        """
        active = bugs_by_status["active_accepted"]
        auto = bugs_by_status["auto_accepted"]
        rejected = bugs_by_status["rejected"]

        triaged_count = active + auto + rejected

        if triaged_count == 0:
            return None  # No triaged bugs to calculate rates from

        active_rate = active / triaged_count
        auto_rate = auto / triaged_count
        rejection_rate = rejected / triaged_count

        # Import settings here to avoid circular import
        from testio_mcp.config import settings

        return {
            "active_acceptance_rate": active_rate,
            "auto_acceptance_rate": auto_rate,
            "rejection_rate": rejection_rate,
            "triaged_count": triaged_count,
            "open_count": bugs_by_status["open"],
            "has_alert": auto_rate > settings.AUTO_ACCEPTANCE_ALERT_THRESHOLD,
        }
