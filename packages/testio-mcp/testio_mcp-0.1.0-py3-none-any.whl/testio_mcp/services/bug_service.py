"""Bug service for exploratory test bug retrieval and filtering operations.

This service handles business logic for bug queries, following
the service layer pattern (ADR-006). It is framework-agnostic and can
be used from MCP tools, REST APIs, CLI, or webhooks.

Implements cache-raw pattern (ADR-011): caches all bugs once per test,
applies filters in-memory. This eliminates cache key explosion and fixes
the continuation token cache-bypass bug from the original implementation.

Responsibilities:
- Bug classification (handles overloaded severity field)
- Client-side filtering (bug_type, severity, status) applied to cached data
- Cache management using BaseService pattern (TTL: 60 seconds)
- Pagination support (continuation tokens) with cache utilization
- Domain exception raising (TestNotFoundException on 404)

Does NOT handle:
- MCP protocol formatting
- User-facing error messages
- HTTP transport concerns
"""

import base64
import json
import logging
from datetime import datetime
from typing import Any

from testio_mcp.exceptions import TestNotFoundException
from testio_mcp.models.schemas import BugAttachment, BugDetails, BugDevice
from testio_mcp.services.base_service import BaseService

logger = logging.getLogger(__name__)

# Pagination limits (ADR-005)
MIN_PAGE_SIZE = 1
MAX_PAGE_SIZE = 1000


class BugService(BaseService):
    """Business logic for bug retrieval and filtering operations.

    This service implements the overloaded severity field classification logic
    and client-side filtering to provide user-friendly bug queries.

    The TestIO API's severity field serves dual purposes:
    1. Bug type classification (visual, content) for non-functional bugs
    2. Severity level (low, high, critical) for functional bugs

    This service handles the classification and filtering logic transparently
    using the cache-raw pattern: caches all bugs once, filters in-memory.

    Example:
        ```python
        service = BugService(client=client, cache=cache)
        bugs = await service.get_test_bugs(
            test_id="109363",
            bug_type="functional",
            severity="critical"
        )
        ```

    Cache Strategy (ADR-011 Cache-Raw Pattern):
        - Cache key: `test:{test_id}:bugs:raw` (one entry per test)
        - Filters applied in-memory (microseconds vs API milliseconds)
        - Eliminates cache key explosion from filter combinations
        - Pagination works with cached data (fixes cache-bypass bug)

    Attributes:
        client: TestIO API client for making requests (inherited)
        cache: Cache instance for storing responses (inherited)
        CACHE_TTL_BUGS: TTL constant for bug data (60 seconds, inherited)
    """

    __test__ = False

    async def get_test_bugs(
        self,
        test_id: int,
        bug_type: str = "all",
        severity: str = "all",
        status: str = "all",
        page_size: int = 100,
        continuation_token: str | None = None,
        custom_report_config_id: str | None = None,
    ) -> dict[str, Any]:
        """Get bugs for a test with filtering by type, severity, and status.

        Uses cache-raw pattern (ADR-011):
        1. Fetches/caches ALL bugs for the test (cache key: test:{id}:bugs:raw)
        2. Applies client-side filtering (bug_type, severity, status)
        3. Paginates filtered results
        4. Returns structured data with pagination info

        This eliminates cache key explosion and fixes the continuation token
        cache-bypass bug found in the original implementation.

        Args:
            test_id: Exploratory test ID (string from user input)
            bug_type: functional|visual|content|custom|all (default: all)
            severity: low|high|critical|all (functional bugs only, default: all)
            status: accepted|rejected|forwarded|auto_accepted|all (default: all)
            page_size: Number of bugs per page (default: 100, max: 1000)
            continuation_token: Token from previous response to get next page
            custom_report_config_id: Filter custom bugs by report configuration ID

        Returns:
            Dictionary with filtered bugs and metadata including pagination

        Raises:
            TestNotFoundException: If test not found (404)
            TestIOAPIError: For other API errors
            ValueError: If continuation_token is invalid or page_size out of range
        """
        # Validate page_size (ADR-005)
        if page_size < MIN_PAGE_SIZE or page_size > MAX_PAGE_SIZE:
            raise ValueError(
                f"❌ page_size {page_size} must be between {MIN_PAGE_SIZE} and {MAX_PAGE_SIZE}\n"
                f"💡 Reduce page_size or use pagination to fetch in chunks"
            )

        # Decode continuation token (if provided)
        start_index = 0
        if continuation_token:
            # STORY-017: Breaking change - reject filter parameters when token provided
            # Filters are preserved from original query and encoded in the token
            provided_filters = []
            if bug_type != "all":
                provided_filters.append("bug_type")
            if severity != "all":
                provided_filters.append("severity")
            if status != "all":
                provided_filters.append("status")
            if custom_report_config_id is not None:
                provided_filters.append("custom_report_config_id")

            if provided_filters:
                raise ValueError(
                    f"Cannot provide filter parameters when using continuation_token. "
                    f"Filters are preserved from the original query. "
                    f"Omit {', '.join(provided_filters)} when using continuation_token."
                )

            try:
                token_data = json.loads(base64.b64decode(continuation_token))

                # Decode compact token format (STORY-017 optimization)
                start_index = token_data["i"]  # start_index
                page_size = token_data["s"]  # page_size

                # Validate test_id matches (prevent token reuse across different queries)
                if token_data["t"] != test_id:
                    raise ValueError("Continuation token is for a different test")

                # SECURITY: Revalidate page_size from token (ADR-005)
                # Prevents crafted tokens from bypassing row limit
                if page_size < MIN_PAGE_SIZE or page_size > MAX_PAGE_SIZE:
                    raise ValueError(
                        f"❌ Invalid continuation token: page_size {page_size} must be between "
                        f"{MIN_PAGE_SIZE} and {MAX_PAGE_SIZE}"
                    )

                # SECURITY: Validate start_index is non-negative
                # Prevents negative indexing or oversized offsets
                if start_index < 0:
                    raise ValueError(
                        f"❌ Invalid continuation token: "
                        f"start_index {start_index} must be non-negative"
                    )

                # STORY-017: Extract filters from token (self-sufficient tokens)
                # Filters use short keys and omit defaults for compression
                token_filters = token_data.get("f", {})
                bug_type = token_filters.get("bt", "all")
                severity = token_filters.get("sv", "all")
                status = token_filters.get("st", "all")
                custom_report_config_id = token_filters.get("cr")

            except (KeyError, json.JSONDecodeError, Exception) as e:
                raise ValueError(f"❌ Invalid continuation token: {e}") from e

        # CACHE-RAW PATTERN: Fetch/cache ALL bugs (no filters in cache key)
        # This fixes the cache-bypass bug and eliminates filter key explosion
        cache_key = self._make_cache_key("test", test_id, "bugs", "raw")
        bugs_response = await self._get_cached_or_fetch(
            cache_key=cache_key,
            fetch_fn=lambda: self.client.get(f"bugs?filter_test_cycle_ids={test_id}"),
            ttl_seconds=self.CACHE_TTL_BUGS,
            transform_404=TestNotFoundException(int(test_id)),
        )

        all_bugs = bugs_response.get("bugs", [])
        total_count = len(all_bugs)

        # Handle empty results (not an error)
        if total_count == 0:
            return {
                "test_id": test_id,
                "total_count": 0,
                "filtered_count": 0,
                "page_size": 0,
                "has_more": False,
                "continuation_token": None,
                "filters_applied": {
                    "bug_type": bug_type,
                    "severity": severity,
                    "status": status,
                    "custom_report_config_id": custom_report_config_id,
                },
                "bugs": [],
            }

        # Apply filters (in-memory, microseconds vs API milliseconds)
        filtered_bugs = self._filter_bugs(
            all_bugs, bug_type, severity, status, custom_report_config_id
        )

        # Paginate filtered results
        return self._paginate(
            test_id=test_id,
            all_bugs=filtered_bugs,
            total_count=total_count,
            start_index=start_index,
            page_size=page_size,
            filters={
                "bug_type": bug_type,
                "severity": severity,
                "status": status,
                "custom_report_config_id": custom_report_config_id,
            },
        )

    def _classify_bug(self, severity_value: str) -> tuple[str, str | None]:
        """Classify bug type and severity level from overloaded severity field.

        The TestIO API's severity field contains either:
        - Bug type (visual, content, custom) for non-functional bugs
        - Severity level (low, high, critical) for functional bugs

        Args:
            severity_value: Raw severity field value from API

        Returns:
            Tuple of (bug_type, severity_level)
            - bug_type: "functional" | "visual" | "content" | "custom"
            - severity_level: "low" | "high" | "critical" | None | "unknown"

        Examples:
            >>> service._classify_bug("visual")
            ('visual', None)
            >>> service._classify_bug("content")
            ('content', None)
            >>> service._classify_bug("custom")
            ('custom', None)
            >>> service._classify_bug("low")
            ('functional', 'low')
            >>> service._classify_bug("critical")
            ('functional', 'critical')
            >>> service._classify_bug("unknown")
            ('functional', 'unknown')
        """
        # Non-functional bug types
        if severity_value == "visual":
            return ("visual", None)
        if severity_value == "content":
            return ("content", None)
        # Custom report bugs (e.g., accessibility, performance testing)
        # These use custom report configurations with specialized fields
        if severity_value == "custom":
            return ("custom", None)

        # Functional bugs with severity levels
        if severity_value in ["low", "high", "critical"]:
            return ("functional", severity_value)

        # Unknown/defensive fallback
        logger.warning(
            f"Unknown severity value: '{severity_value}' - treating as functional/unknown"
        )
        return ("functional", "unknown")

    def _filter_bugs(
        self,
        bugs: list[dict[str, Any]],
        bug_type: str,
        severity: str,
        status: str,
        custom_report_config_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Client-side bug filtering with classification.

        Since TestIO API doesn't support filtering by bug type or severity,
        we implement client-side filtering with proper classification.

        Args:
            bugs: All bugs from API
            bug_type: functional|visual|content|custom|all
            severity: low|high|critical|all (only for functional)
            status: accepted|rejected|forwarded|auto_accepted|all (STORY-005c AC5)
            custom_report_config_id: Filter custom bugs by report configuration ID (optional)

        Returns:
            Filtered list of bugs
        """
        filtered = []

        for bug in bugs:
            severity_value = bug.get("severity", "")
            bug_status = bug.get("status", "")
            auto_accepted = bug.get("auto_accepted")  # STORY-005c: extract auto_accepted field

            # Classify bug type and severity level
            classified_type, severity_level = self._classify_bug(severity_value)

            # Filter 1: Bug Type
            if bug_type != "all":
                if bug_type == "functional":
                    # Include only functional bugs (severity in low/high/critical)
                    if classified_type != "functional":
                        continue
                elif bug_type == "visual":
                    # Include only visual bugs (severity == "visual")
                    if severity_value != "visual":
                        continue
                elif bug_type == "content":
                    # Include only content bugs (severity == "content")
                    if severity_value != "content":
                        continue
                elif bug_type == "custom":
                    # Include only custom report bugs (severity == "custom")
                    if severity_value != "custom":
                        continue

            # Filter 2: Severity Level (ONLY for functional bugs)
            if severity != "all" and classified_type == "functional":
                if severity_level != severity:
                    continue

            # Filter 3: Status with auto-acceptance support (STORY-005c AC5)
            if status != "all":
                if status == "accepted":
                    # Active-accepted only: status="accepted" AND auto_accepted=false
                    if bug_status != "accepted" or auto_accepted is True:
                        continue
                elif status == "auto_accepted":
                    # Auto-accepted only: status="accepted" AND auto_accepted=true
                    if bug_status != "accepted" or auto_accepted is not True:
                        continue
                elif status == "forwarded":
                    # Open bugs awaiting triage
                    if bug_status != "forwarded":
                        continue
                elif status == "rejected":
                    # Rejected bugs
                    if bug_status != "rejected":
                        continue
                # else: status is "all", no filtering

            # Filter 4: Custom Report Configuration ID
            # When specified, ONLY return custom bugs matching the configuration ID
            if custom_report_config_id is not None:
                if severity_value == "custom":
                    # Extract custom report configuration IDs from bug feature
                    feature = bug.get("feature", {})
                    custom_configs = feature.get("custom_report_configurations", [])
                    config_ids = [str(config.get("id")) for config in custom_configs]

                    # Only include bug if it matches the requested configuration ID
                    if custom_report_config_id not in config_ids:
                        continue
                else:
                    # Not a custom bug, exclude when config_id filter is active
                    continue

            # Bug passed all filters
            filtered.append(bug)

        return filtered

    def _paginate(
        self,
        test_id: int,
        all_bugs: list[dict[str, Any]],
        total_count: int,
        start_index: int,
        page_size: int,
        filters: dict[str, Any],
    ) -> dict[str, Any]:
        """Paginate filtered bugs and generate response with continuation token.

        Helper method that eliminates code duplication between cache hit and
        cache miss paths.

        Args:
            test_id: Test ID for continuation token validation
            all_bugs: Filtered bugs to paginate
            total_count: Total bug count before filtering
            start_index: Starting index for current page
            page_size: Number of bugs per page
            filters: Applied filters for continuation token validation

        Returns:
            Dictionary with paginated bugs and metadata
        """
        # Paginate filtered results
        end_index = start_index + page_size
        page_bugs = all_bugs[start_index:end_index]
        has_more = end_index < len(all_bugs)

        # Build detailed bug objects
        bug_details = [self._build_bug_details(bug) for bug in page_bugs]

        # Generate continuation token for next page
        next_token = None
        if has_more:
            # Optimize token size by using short keys and omitting defaults (STORY-017)
            token_data: dict[str, Any] = {
                "t": test_id,  # test_id (int)
                "i": end_index,  # start_index (int)
                "s": page_size,  # page_size (int)
            }

            # Only include non-default filters (reduces token size by ~65%)
            f: dict[str, str] = {}
            if filters["bug_type"] != "all":
                f["bt"] = filters["bug_type"]
            if filters["severity"] != "all":
                f["sv"] = filters["severity"]
            if filters["status"] != "all":
                f["st"] = filters["status"]
            if filters["custom_report_config_id"] is not None:
                f["cr"] = filters["custom_report_config_id"]

            if f:  # Only add filters key if non-empty
                token_data["f"] = f

            next_token = base64.b64encode(json.dumps(token_data).encode()).decode()

        return {
            "test_id": test_id,
            "total_count": total_count,
            "filtered_count": len(all_bugs),
            "page_size": len(page_bugs),
            "has_more": has_more,
            "continuation_token": next_token,
            "filters_applied": filters,
            "bugs": [bug.model_dump(exclude_none=True) for bug in bug_details],
        }

    def _build_bug_details(self, bug: dict[str, Any]) -> BugDetails:
        """Transform API bug data into BugDetails model.

        Extracts report.content field if present (typically for custom bugs
        like accessibility reports, purchase reports, etc.).

        Args:
            bug: Raw bug data from API

        Returns:
            BugDetails Pydantic model with classified bug_type and severity_level
        """
        classified_type, severity_level = self._classify_bug(bug.get("severity", ""))

        # Parse datetime fields
        created_at_str = bug.get("created_at")
        created_at = (
            datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            if created_at_str
            else datetime.now()
        )

        exported_at_str = bug.get("exported_at")
        exported_at = (
            datetime.fromisoformat(exported_at_str.replace("Z", "+00:00"))
            if exported_at_str
            else None
        )

        # Extract custom report content if present (STORY-014)
        # Custom bugs (accessibility, purchase reports, etc.) have structured
        # data in report.content that contains the actual findings
        report_content = None
        if bug.get("report") and bug["report"].get("content"):
            report_content = bug["report"]["content"]

        return BugDetails(
            id=str(bug["id"]),
            title=bug["title"],
            bug_type=classified_type,
            severity_level=severity_level,
            status=bug.get("status", "unknown"),
            location=bug.get("location"),
            expected_result=bug.get("expected_result"),
            actual_result=bug.get("actual_result"),
            steps=bug.get("steps", []),
            author_name=bug.get("author", {}).get("name", "Unknown"),
            tester_name=bug.get("tester", {}).get("name") if bug.get("tester") else None,
            devices=[
                BugDevice(
                    device_name=d.get("device_name", "Unknown"),
                    os_name=d.get("os_name", "Unknown"),
                    os_version=d.get("os_version", "Unknown"),
                )
                for d in bug.get("devices", [])
            ],
            attachments=[
                BugAttachment(
                    id=str(a.get("id", "")),
                    url=a.get("url", ""),
                    type=a.get("type", "screenshot"),
                )
                for a in bug.get("attachments", [])
            ],
            known=bug.get("known", False),
            exported_at=exported_at,
            created_at=created_at,
            report_content=report_content,
        )
