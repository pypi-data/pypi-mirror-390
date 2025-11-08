"""Report service for generating status reports from multiple tests.

This service handles business logic for report generation, following
the service layer pattern (ADR-006). It is framework-agnostic and can
be used from MCP tools, REST APIs, CLI, or webhooks.

Responsibilities:
- Concurrent fetching of test data via TestService
- Report formatting (markdown, text, JSON)
- Aggregate metrics calculation
- Critical issues identification
- Recommendations generation

Does NOT handle:
- MCP protocol formatting
- User-facing error messages
- HTTP transport concerns
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any, Literal

from testio_mcp.services.base_service import BaseService
from testio_mcp.services.test_service import TestService


class ReportService(BaseService):
    """Business logic for generating status reports from multiple tests.

    Inherits from BaseService to get standard dependency injection and
    cache helper methods.

    This service demonstrates cross-service communication by using TestService
    to fetch individual test data. It aggregates that data into formatted reports
    suitable for stakeholder communication.

    Example:
        ```python
        service = ReportService(client=client, cache=cache)
        report = await service.generate_report(
            test_ids=["109363", "109364"],
            format="markdown"
        )
        ```
    """

    __test__ = False

    async def generate_report(
        self,
        test_ids: list[int],
        format: Literal["markdown", "text", "json"] = "markdown",
    ) -> str:
        """Generate executive summary report for stakeholder communication.

        Args:
            test_ids: List of test IDs to include (1-20 tests)
            format: Output format - markdown, text, or json

        Returns:
            Formatted status report as string

        Raises:
            ValueError: If test_ids is empty or all tests fail to load
        """
        if not test_ids:
            raise ValueError("test_ids cannot be empty")

        # Fetch all test data concurrently
        successful_tests, failed_tests = await self._fetch_test_data(test_ids)

        # Check if all tests failed
        if not successful_tests:
            raise ValueError(
                f"Failed to generate report - all {len(failed_tests)} tests failed to load"
            )

        # Generate report in requested format
        if format == "markdown":
            return self._generate_markdown_report(successful_tests, failed_tests)
        elif format == "text":
            return self._generate_text_report(successful_tests, failed_tests)
        else:  # json
            return self._generate_json_report(successful_tests, failed_tests)

    async def _fetch_test_data(
        self, test_ids: list[int]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str | int]]]:
        """Fetch test data concurrently for all test IDs.

        Uses TestService for each test (cross-service communication).

        Args:
            test_ids: List of test IDs

        Returns:
            Tuple of (successful_tests, failed_tests)
        """
        # Create test service instance for fetching
        test_service = TestService(client=self.client, cache=self.cache)

        # Fetch all test data concurrently with timeout
        # Convert string test_ids to integers for TestService
        try:
            results = await asyncio.wait_for(
                asyncio.gather(
                    *[test_service.get_test_status(int(test_id)) for test_id in test_ids],
                    return_exceptions=True,
                ),
                timeout=30.0,  # 30 second total timeout
            )
        except TimeoutError as e:
            raise ValueError(
                f"Report generation timed out after 30 seconds. "
                f"Requested {len(test_ids)} tests - too many for single report. "
                f"Reduce number of tests (max recommended: 10)."
            ) from e

        # Separate successful results from errors
        successful_tests: list[dict[str, Any]] = []
        failed_tests: list[dict[str, str | int]] = []  # test_id is int, error is str
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                failed_tests.append(
                    {
                        "test_id": test_ids[idx],  # int
                        "error": str(result),  # str
                    }
                )
            else:
                # Type narrowing: result is dict[str, Any] when not Exception
                assert isinstance(result, dict), "Result must be dict when not Exception"
                successful_tests.append(result)

        return successful_tests, failed_tests

    def _generate_markdown_report(
        self, tests: list[dict[str, Any]], failed_tests: list[dict[str, Any]]
    ) -> str:
        """Generate markdown formatted report."""
        report = []
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

        # Header
        report.append("# Test Status Report")
        report.append(f"Generated: {now}")
        report.append("")

        # Test overview table (STORY-005c AC6: Add Active/Auto/Open columns)
        report.append("## Test Overview")
        report.append("")

        # Check if acceptance rates available (determines table columns)
        has_acceptance_rates = any(t["bugs"].get("acceptance_rates") is not None for t in tests)

        # Build table header with acceptance status columns
        if has_acceptance_rates:
            # Production: Show Active/Auto/Total/Rejected/Open
            report.append(
                "| Test ID | Title | Status | Bugs | Active | Auto | Total Accept | Rejected | Open |"  # noqa: E501
            )
            report.append(
                "|---------|-------|--------|------|--------|------|--------------|----------|------|"
            )
        else:
            # Staging: Show simpler Accepted/Rejected/Open
            report.append("| Test ID | Title | Status | Bugs | Accepted | Rejected | Open |")
            report.append("|---------|-------|--------|------|----------|----------|------|")

        for test_data in tests:
            test = test_data["test"]
            bugs = test_data["bugs"]
            bug_status = bugs["by_status"]

            if has_acceptance_rates:
                # Production table with auto-acceptance breakdown
                auto_count = bug_status.get("auto_accepted", 0)
                # Add warning emoji if auto count > 0 and rate exceeds threshold
                from testio_mcp.config import settings

                auto_display = (
                    f"{auto_count}⚠️"
                    if auto_count > 0 and bugs.get("acceptance_rates", {}).get("has_alert", False)
                    else str(auto_count)
                )

                row = (
                    f"| {test['id']} | {test['title']} | {test['status']} | "
                    f"{bugs['total_count']} | "
                    f"{bug_status.get('active_accepted', 0)} | "
                    f"{auto_display} | "
                    f"{bug_status.get('total_accepted', 0)} | "
                    f"{bug_status.get('rejected', 0)} | "
                    f"{bug_status.get('open', 0)} |"
                )
            else:
                # Staging table (no auto-acceptance breakdown)
                row = (
                    f"| {test['id']} | {test['title']} | {test['status']} | "
                    f"{bugs['total_count']} | "
                    f"{bug_status.get('total_accepted', 0)} | "
                    f"{bug_status.get('rejected', 0)} | "
                    f"{bug_status.get('open', 0)} |"
                )
            report.append(row)

        report.append("")

        # Key metrics (STORY-005c AC6: Add acceptance rates)
        total_bugs = sum(t["bugs"]["total_count"] for t in tests)
        critical_bugs = sum(t["bugs"]["by_severity"].get("critical", 0) for t in tests)
        high_bugs = sum(t["bugs"]["by_severity"].get("high", 0) for t in tests)
        custom_bugs = sum(t["bugs"]["by_severity"].get("custom", 0) for t in tests)
        passed_review = sum(
            1 for t in tests if t["test"].get("review_status") == "review_successful"
        )

        # Calculate aggregated acceptance metrics (new structure STORY-005c AC0)
        active_accepted = sum(t["bugs"]["by_status"].get("active_accepted", 0) for t in tests)
        auto_accepted = sum(t["bugs"]["by_status"].get("auto_accepted", 0) for t in tests)
        total_accepted = sum(t["bugs"]["by_status"].get("total_accepted", 0) for t in tests)
        rejected = sum(t["bugs"]["by_status"].get("rejected", 0) for t in tests)
        open_bugs = sum(t["bugs"]["by_status"].get("open", 0) for t in tests)

        # Check if acceptance rates are available (production vs staging)
        has_acceptance_rates = any(t["bugs"].get("acceptance_rates") is not None for t in tests)

        # Calculate aggregate acceptance rates if available
        triaged_total = active_accepted + auto_accepted + rejected
        active_rate = (active_accepted / triaged_total * 100) if triaged_total > 0 else 0
        auto_rate = (auto_accepted / triaged_total * 100) if triaged_total > 0 else 0
        rejection_rate = (rejected / triaged_total * 100) if triaged_total > 0 else 0

        report.append("## Key Metrics")
        report.append(f"- **Total Tests**: {len(tests)}")
        report.append(f"- **Total Bugs Found**: {total_bugs}")
        report.append(f"- **Critical Bugs**: {critical_bugs}")
        report.append(f"- **High Severity Bugs**: {high_bugs}")
        if custom_bugs > 0:
            report.append(f"- **Custom Report Bugs**: {custom_bugs}")
        if passed_review > 0:
            pct = passed_review / len(tests) * 100
            report.append(f"- **Tests Passed Review**: {passed_review}/{len(tests)} ({pct:.0f}%)")

        # Add acceptance rate metrics (STORY-005c AC6)
        if has_acceptance_rates and triaged_total > 0:
            report.append(
                f"- **Active Acceptance Rate**: {active_rate:.0f}% ({active_accepted}/{triaged_total} triaged)"  # noqa: E501
            )
            # Add warning emoji if auto-acceptance rate exceeds threshold
            from testio_mcp.config import settings

            auto_warning = (
                " ⚠️" if auto_rate > (settings.AUTO_ACCEPTANCE_ALERT_THRESHOLD * 100) else ""
            )
            report.append(
                f"- **Auto-Acceptance Rate**: {auto_rate:.0f}% ({auto_accepted}/{triaged_total} triaged){auto_warning}"  # noqa: E501
            )
            report.append(
                f"- **Rejection Rate**: {rejection_rate:.0f}% ({rejected}/{triaged_total} triaged)"
            )
            report.append(f"- **Open Bugs**: {open_bugs} (awaiting customer triage)")
        elif total_accepted > 0:
            # Fallback for staging (no acceptance rates available)
            pct = total_accepted / total_bugs * 100
            report.append(f"- **Bugs Accepted**: {total_accepted}/{total_bugs} ({pct:.0f}%)")
        report.append("")

        # Quality Signals section (STORY-005c AC3)
        if has_acceptance_rates and triaged_total > 0:
            report.append("## Quality Signals")
            report.append("")
            report.append("### Feedback Loop Health")

            # Active acceptance (good if > 60%)
            active_emoji = "✅" if active_rate > 60 else "⚠️"
            report.append(
                f"- {active_emoji} **Active Acceptance**: {active_rate:.0f}% (customer reviewing and accepting)"  # noqa: E501
            )

            # Auto-acceptance (derive bands from configurable threshold)
            # Healthy: < threshold/2, Warning: threshold/2 to threshold, Critical: > threshold
            from testio_mcp.config import settings

            threshold_pct = settings.AUTO_ACCEPTANCE_ALERT_THRESHOLD * 100
            warning_threshold_pct = threshold_pct / 2
            if auto_rate > threshold_pct:
                auto_emoji = "🚨"
            elif auto_rate > warning_threshold_pct:
                auto_emoji = "⚠️"
            else:
                auto_emoji = "✅"
            report.append(
                f"- {auto_emoji} **Auto-Acceptance**: {auto_rate:.0f}% (timeout after 10 days - feedback loop {'degraded' if auto_rate > threshold_pct else 'healthy'})"  # noqa: E501
            )

            # Rejection rate (good if > 5%)
            rejection_emoji = "✅" if rejection_rate > 5 else "ℹ️"
            report.append(
                f"- {rejection_emoji} **Rejection**: {rejection_rate:.0f}% (customer reviewing and rejecting)"  # noqa: E501
            )
            report.append("")

            # Alert if auto-acceptance exceeds threshold (STORY-005c AC4)
            if auto_rate > threshold_pct:
                report.append(
                    f"⚠️ **Alert**: Auto-acceptance rate of {auto_rate:.0f}% exceeds threshold ({threshold_pct:.0f}%)."  # noqa: E501
                )
                report.append(
                    "This indicates customers are not actively triaging bugs, which kills opportunities"  # noqa: E501
                )
                report.append("for test refinement based on feedback.")
                report.append("")
                report.append(
                    f"**Recommendation**: Engage customers to actively review the {auto_accepted} auto-accepted bugs and"  # noqa: E501
                )
                report.append(f"the {open_bugs} open bugs awaiting triage.")
                report.append("")
            else:
                report.append(
                    "**Status:** Feedback loop is healthy. Customers are actively triaging bugs."
                )
                report.append("")
        elif not has_acceptance_rates:
            # Staging environment notice
            report.append("## Quality Signals")
            report.append("")
            report.append(
                "ℹ️ **Note**: Auto-acceptance metrics unavailable in this environment (staging)."
            )
            report.append("Active vs auto-acceptance breakdown requires production API.")
            report.append("")

        # Critical issues
        report.append("## Critical Issues Requiring Attention")
        report.append("")
        for test_data in tests:
            test = test_data["test"]
            bugs = test_data["bugs"]
            critical_count = bugs["by_severity"].get("critical", 0)
            high_count = bugs["by_severity"].get("high", 0)
            has_critical_issues = (
                critical_count > 0 or high_count > 0 or test["status"] == "running"
            )

            if has_critical_issues:
                report.append(f"### Test {test['id']} - {test['title']}")
                if critical_count > 0:
                    report.append(f"- ⚠️ {critical_count} critical bugs found")
                if high_count > 0:
                    report.append(f"- ⚠️ {high_count} high severity bug(s) found")
                if test["status"] == "running":
                    report.append("- ℹ️ Test still running, bugs found so far")
                report.append("")

        # Overall progress
        completed = sum(1 for t in tests if t["test"]["status"] in ["archived", "locked"])
        report.append("## Overall Progress")
        report.append(
            f"- **Tests Completed**: {completed}/{len(tests)} ({completed / len(tests) * 100:.0f}%)"
        )
        if passed_review > 0:
            completed_with_review = sum(
                1 for t in tests if t["test"].get("review_status") == "review_successful"
            )
            if completed > 0:
                pct = completed_with_review / completed * 100
                report.append(
                    f"- **Review Success Rate**: {completed_with_review}/{completed} ({pct:.0f}%)"
                )
            else:
                pct = completed_with_review / len(tests) * 100
                report.append(
                    f"- **Review Success Rate**: {completed_with_review}/{len(tests)} ({pct:.0f}%)"
                )
        report.append(f"- **Average Bugs per Test**: {total_bugs / len(tests):.1f}")
        if total_accepted > 0 and not has_acceptance_rates:
            # Fallback for staging: Show simple acceptance rate
            pct = total_accepted / total_bugs * 100
            report.append(f"- **Bug Acceptance Rate**: {total_accepted}/{total_bugs} ({pct:.0f}%)")
        report.append("")

        # Recommendations
        recommendations = self._generate_recommendations(tests)
        if recommendations:
            report.append("## Recommendations")
            for rec in recommendations:
                report.append(f"- {rec}")
            report.append("")

        # Warnings about failed tests
        if failed_tests:
            report.append("## ⚠️ Warnings")
            for failed in failed_tests:
                report.append(f"- Test {failed['test_id']}: {failed['error']}")
            report.append("")

        report.append("---")
        report.append("*Report generated by TestIO MCP Server*")

        return "\n".join(report)

    def _generate_text_report(
        self, tests: list[dict[str, Any]], failed_tests: list[dict[str, Any]]
    ) -> str:
        """Generate plain text formatted report."""
        report = []
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

        # Header
        report.append("=" * 40)
        report.append("TEST STATUS REPORT")
        report.append("=" * 40)
        report.append(f"Generated: {now}")
        report.append("")

        # Test overview table
        report.append("TEST OVERVIEW")
        report.append("-" * 40)
        report.append("Test ID  | Title            | Status   | Review  | Bugs | Critical")
        report.append("-" * 40)

        for test_data in tests:
            test = test_data["test"]
            bugs = test_data["bugs"]
            review_status = (
                "Passed" if test.get("review_status") == "review_successful" else "Pending"
            )
            critical_count = bugs["by_severity"].get("critical", 0)
            report.append(
                f"{test['id']:<8} | {test['title'][:15]:<15} | "
                f"{test['status']:<8} | {review_status:<7} | "
                f"{bugs['total_count']:<4} | {critical_count}"
            )

        report.append("")

        # Key metrics (STORY-005c: Add acceptance rates to text format)
        total_bugs = sum(t["bugs"]["total_count"] for t in tests)
        critical_bugs = sum(t["bugs"]["by_severity"].get("critical", 0) for t in tests)
        high_bugs = sum(t["bugs"]["by_severity"].get("high", 0) for t in tests)
        custom_bugs = sum(t["bugs"]["by_severity"].get("custom", 0) for t in tests)
        passed_review = sum(
            1 for t in tests if t["test"].get("review_status") == "review_successful"
        )

        # Calculate acceptance metrics (new structure)
        active_accepted = sum(t["bugs"]["by_status"].get("active_accepted", 0) for t in tests)
        auto_accepted = sum(t["bugs"]["by_status"].get("auto_accepted", 0) for t in tests)
        total_accepted = sum(t["bugs"]["by_status"].get("total_accepted", 0) for t in tests)
        rejected = sum(t["bugs"]["by_status"].get("rejected", 0) for t in tests)
        open_bugs = sum(t["bugs"]["by_status"].get("open", 0) for t in tests)
        has_acceptance_rates = any(t["bugs"].get("acceptance_rates") is not None for t in tests)

        triaged_total = active_accepted + auto_accepted + rejected
        active_rate = (active_accepted / triaged_total * 100) if triaged_total > 0 else 0
        auto_rate = (auto_accepted / triaged_total * 100) if triaged_total > 0 else 0
        rejection_rate = (rejected / triaged_total * 100) if triaged_total > 0 else 0

        report.append("KEY METRICS")
        report.append("-" * 40)
        report.append(f"Total Tests:               {len(tests)}")
        report.append(f"Total Bugs Found:          {total_bugs}")
        report.append(f"Critical Bugs:             {critical_bugs}")
        report.append(f"High Severity Bugs:        {high_bugs}")
        if custom_bugs > 0:
            report.append(f"Custom Report Bugs:        {custom_bugs}")
        if passed_review > 0:
            pct = passed_review / len(tests) * 100
            report.append(f"Tests Passed Review:       {passed_review}/{len(tests)} ({pct:.0f}%)")

        # Add acceptance rates if available
        if has_acceptance_rates and triaged_total > 0:
            report.append(
                f"Active Acceptance Rate:    {active_rate:.0f}% ({active_accepted}/{triaged_total})"
            )
            report.append(
                f"Auto-Acceptance Rate:      {auto_rate:.0f}% ({auto_accepted}/{triaged_total})"
            )
            report.append(
                f"Rejection Rate:            {rejection_rate:.0f}% ({rejected}/{triaged_total})"
            )
            report.append(f"Open Bugs:                 {open_bugs}")
        elif total_accepted > 0:
            pct = total_accepted / total_bugs * 100
            report.append(f"Bugs Accepted:             {total_accepted}/{total_bugs} ({pct:.0f}%)")
        report.append("")

        # Critical issues
        report.append("CRITICAL ISSUES")
        report.append("-" * 40)
        for test_data in tests:
            test = test_data["test"]
            bugs = test_data["bugs"]
            critical_count = bugs["by_severity"].get("critical", 0)
            high_count = bugs["by_severity"].get("high", 0)
            has_critical_issues = (
                critical_count > 0 or high_count > 0 or test["status"] == "running"
            )

            if has_critical_issues:
                report.append(f"[Test {test['id']}]")
                if critical_count > 0:
                    report.append(f"- {critical_count} critical bugs found")
                if high_count > 0:
                    report.append(f"- {high_count} high severity bug(s)")
                if test["status"] == "running":
                    report.append("- Test still running")
                report.append("")

        # Overall progress
        completed = sum(1 for t in tests if t["test"]["status"] in ["archived", "locked"])
        report.append("OVERALL PROGRESS")
        report.append("-" * 40)
        pct = completed / len(tests) * 100
        report.append(f"Tests Completed:          {completed}/{len(tests)} ({pct:.0f}%)")
        if passed_review > 0:
            completed_with_review = sum(
                1 for t in tests if t["test"].get("review_status") == "review_successful"
            )
            if completed > 0:
                pct = completed_with_review / completed * 100
                report.append(
                    f"Review Success Rate:       {completed_with_review}/{completed} ({pct:.0f}%)"
                )
            else:
                pct = completed_with_review / len(tests) * 100
                report.append(
                    f"Review Success Rate:       {completed_with_review}/{len(tests)} ({pct:.0f}%)"
                )
        report.append(f"Average Bugs per Test:    {total_bugs / len(tests):.1f}")
        if total_accepted > 0 and not has_acceptance_rates:
            # Fallback for staging: Show simple acceptance rate
            pct = total_accepted / total_bugs * 100
            report.append(f"Bug Acceptance Rate:       {total_accepted}/{total_bugs} ({pct:.0f}%)")
        report.append("")

        # Recommendations
        recommendations = self._generate_recommendations(tests)
        if recommendations:
            report.append("RECOMMENDATIONS")
            report.append("-" * 40)
            for rec in recommendations:
                report.append(f"- {rec}")
            report.append("")

        # Warnings about failed tests
        if failed_tests:
            report.append("WARNINGS")
            report.append("-" * 40)
            for failed in failed_tests:
                report.append(f"- Test {failed['test_id']}: {failed['error']}")
            report.append("")

        report.append("=" * 40)
        report.append("Report generated by TestIO MCP Server")
        report.append("=" * 40)

        return "\n".join(report)

    def _generate_json_report(
        self, tests: list[dict[str, Any]], failed_tests: list[dict[str, Any]]
    ) -> str:
        """Generate JSON formatted report."""
        now = datetime.now(UTC).isoformat()

        # Calculate summary metrics
        total_bugs = sum(t["bugs"]["total_count"] for t in tests)
        bugs_by_severity = {
            "critical": sum(t["bugs"]["by_severity"].get("critical", 0) for t in tests),
            "high": sum(t["bugs"]["by_severity"].get("high", 0) for t in tests),
            "low": sum(t["bugs"]["by_severity"].get("low", 0) for t in tests),
            "visual": sum(t["bugs"]["by_severity"].get("visual", 0) for t in tests),
            "content": sum(t["bugs"]["by_severity"].get("content", 0) for t in tests),
            "custom": sum(t["bugs"]["by_severity"].get("custom", 0) for t in tests),
        }
        # Updated bug status structure (STORY-005c AC0)
        bugs_by_status = {
            "active_accepted": sum(t["bugs"]["by_status"].get("active_accepted", 0) for t in tests),
            "auto_accepted": sum(t["bugs"]["by_status"].get("auto_accepted", 0) for t in tests),
            "total_accepted": sum(t["bugs"]["by_status"].get("total_accepted", 0) for t in tests),
            "rejected": sum(t["bugs"]["by_status"].get("rejected", 0) for t in tests),
            "open": sum(t["bugs"]["by_status"].get("open", 0) for t in tests),
        }

        # Calculate acceptance rates if available (STORY-005c AC2)
        has_acceptance_rates = any(t["bugs"].get("acceptance_rates") is not None for t in tests)
        aggregate_acceptance_rates = None
        if has_acceptance_rates:
            triaged_total = (
                bugs_by_status["active_accepted"]
                + bugs_by_status["auto_accepted"]
                + bugs_by_status["rejected"]
            )
            if triaged_total > 0:
                active_rate = bugs_by_status["active_accepted"] / triaged_total
                auto_rate = bugs_by_status["auto_accepted"] / triaged_total
                rejection_rate = bugs_by_status["rejected"] / triaged_total
                from testio_mcp.config import settings

                aggregate_acceptance_rates = {
                    "active_acceptance_rate": active_rate,
                    "auto_acceptance_rate": auto_rate,
                    "rejection_rate": rejection_rate,
                    "triaged_count": triaged_total,
                    "open_count": bugs_by_status["open"],
                    "has_alert": auto_rate > settings.AUTO_ACCEPTANCE_ALERT_THRESHOLD,
                }
        tests_completed = sum(1 for t in tests if t["test"]["status"] in ["archived", "locked"])
        tests_in_progress = sum(1 for t in tests if t["test"]["status"] == "running")
        passed_review = sum(
            1 for t in tests if t["test"].get("review_status") == "review_successful"
        )
        review_pass_rate = passed_review / tests_completed if tests_completed > 0 else 0.0
        bug_acceptance_rate = (
            bugs_by_status["total_accepted"] / total_bugs if total_bugs > 0 else 0.0
        )

        # Build test summaries
        test_summaries = []
        for test_data in tests:
            test = test_data["test"]
            bugs = test_data["bugs"]
            critical_issues = []

            critical_count = bugs["by_severity"].get("critical", 0)
            high_count = bugs["by_severity"].get("high", 0)
            if critical_count > 0:
                critical_issues.append(f"{critical_count} critical bugs found")
            if high_count > 0:
                critical_issues.append(f"{high_count} high severity bug(s) found")
            if test["status"] == "running":
                critical_issues.append(
                    f"Test still running, {bugs['total_count']} bugs found so far"
                )
            if not critical_issues:
                critical_issues.append("Awaiting review completion")

            test_summaries.append(
                {
                    "test_id": str(test["id"]),
                    "title": test["title"],
                    "status": test["status"],
                    "review_status": test.get("review_status"),
                    "bug_summary": {
                        "total": bugs["total_count"],
                        "critical": bugs["by_severity"].get("critical", 0),
                        "high": bugs["by_severity"].get("high", 0),
                        "low": bugs["by_severity"].get("low", 0),
                        "visual": bugs["by_severity"].get("visual", 0),
                        "content": bugs["by_severity"].get("content", 0),
                        "custom": bugs["by_severity"].get("custom", 0),
                    },
                    "critical_issues": critical_issues,
                }
            )

        # Generate recommendations
        recommendations = self._generate_recommendations(tests)

        # Build quality signals for JSON (STORY-005c AC3)
        quality_signals = None
        if aggregate_acceptance_rates:
            auto_rate = aggregate_acceptance_rates["auto_acceptance_rate"]
            from testio_mcp.config import settings

            threshold = settings.AUTO_ACCEPTANCE_ALERT_THRESHOLD

            alert_message = None
            if aggregate_acceptance_rates["has_alert"]:
                alert_message = (
                    f"Auto-acceptance rate of {auto_rate * 100:.0f}% exceeds threshold ({threshold * 100:.0f}%). "  # noqa: E501
                    f"This indicates customers are not actively triaging bugs, which kills opportunities "  # noqa: E501
                    f"for test refinement based on feedback."
                )

            quality_signals = {
                "active_acceptance": {
                    "rate": aggregate_acceptance_rates["active_acceptance_rate"],
                    "status": "healthy"
                    if aggregate_acceptance_rates["active_acceptance_rate"] > 0.6
                    else "warning",
                },
                "auto_acceptance": {
                    "rate": auto_rate,
                    "status": "healthy"
                    if auto_rate < (settings.AUTO_ACCEPTANCE_ALERT_THRESHOLD / 2)
                    else (
                        "warning"
                        if auto_rate < settings.AUTO_ACCEPTANCE_ALERT_THRESHOLD
                        else "critical"
                    ),
                    "alert_triggered": aggregate_acceptance_rates["has_alert"],
                },
                "rejection": {
                    "rate": aggregate_acceptance_rates["rejection_rate"],
                    "status": "healthy"
                    if aggregate_acceptance_rates["rejection_rate"] > 0.05
                    else "low",
                },
                "alert_message": alert_message,
            }

        # Build final JSON structure
        report_data = {
            "report_type": "test_status_summary",
            "generated_at": now,
            "summary": {
                "total_tests": len(tests),
                "tests_completed": tests_completed,
                "tests_in_progress": tests_in_progress,
                "total_bugs": total_bugs,
                "bugs_by_severity": bugs_by_severity,
                "bugs_by_status": bugs_by_status,
                "acceptance_rates": aggregate_acceptance_rates,  # STORY-005c AC2
                "review_pass_rate": review_pass_rate,
                "bug_acceptance_rate": bug_acceptance_rate,
            },
            "quality_signals": quality_signals,  # STORY-005c AC3
            "tests": test_summaries,
            "recommendations": recommendations,
            "failed_tests": failed_tests,
        }

        return json.dumps(report_data, indent=2)

    def _generate_recommendations(self, tests: list[dict[str, Any]]) -> list[str]:
        """Generate actionable recommendations based on test data.

        Args:
            tests: List of test data dictionaries

        Returns:
            List of recommendation strings
        """
        recommendations = []

        for test_data in tests:
            test = test_data["test"]
            bugs = test_data["bugs"]
            critical_count = bugs["by_severity"].get("critical", 0)

            if critical_count > 0:
                recommendations.append(
                    f"Review {critical_count} critical bug(s) from Test "
                    f"{test['id']} for priority action"
                )

            if test["status"] == "running":
                bug_count = bugs["total_count"]
                recommendations.append(
                    f"Monitor Test {test['id']} as it completes ({bug_count} bugs pending review)"
                )

        # Add general recommendations
        rejected_count = sum(t["bugs"]["by_status"].get("rejected", 0) for t in tests)
        if rejected_count > 0:
            recommendations.append("Review rejected bugs to identify patterns")

        return recommendations
