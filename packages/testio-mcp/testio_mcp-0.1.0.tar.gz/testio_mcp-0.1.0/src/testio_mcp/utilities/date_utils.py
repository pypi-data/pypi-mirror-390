"""Date parsing utilities for flexible date input handling.

This module provides utilities for parsing various date formats including:
- ISO 8601 dates (YYYY-MM-DD)
- Business terms (today, yesterday, last 30 days, this quarter, etc.)
- Simple relative dates (3 days ago, 5 days ago)

Performance characteristics:
- Business terms: O(1) dictionary lookup (~1μs)
- ISO 8601: strptime parsing (~1μs)
- Natural language: dateutil parsing (~100μs, fallback only)
"""

import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta
from fastmcp.exceptions import ToolError


def _get_quarter_start(date: datetime) -> datetime:
    """Get the start date of the quarter containing the given date.

    Quarters are calendar-based:
    - Q1: Jan-Mar (starts Jan 1)
    - Q2: Apr-Jun (starts Apr 1)
    - Q3: Jul-Sep (starts Jul 1)
    - Q4: Oct-Dec (starts Oct 1)

    Args:
        date: Date to find quarter start for

    Returns:
        Datetime at the start of the quarter (day 1, 00:00:00)

    Example:
        >>> _get_quarter_start(datetime(2024, 5, 15))
        datetime(2024, 4, 1, 0, 0, 0)  # Q2 starts Apr 1
    """
    quarter_month = ((date.month - 1) // 3) * 3 + 1
    return date.replace(month=quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)


def _get_week_start(date: datetime) -> datetime:
    """Get the start date of the ISO 8601 week containing the given date.

    ISO 8601 weeks start on Monday (weekday 0).

    Args:
        date: Date to find week start for

    Returns:
        Datetime at the start of the week (Monday, 00:00:00)

    Example:
        >>> _get_week_start(datetime(2024, 11, 6))  # Wednesday
        datetime(2024, 11, 4, 0, 0, 0)  # Previous Monday
    """
    days_since_monday = date.weekday()
    monday = date - timedelta(days=days_since_monday)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


# Business terms dictionary with lambda functions for date calculation
# Performance: O(1) lookup, fastest parsing method
# All dates are UTC-aware to ensure correct timezone handling
BUSINESS_TERMS: dict[str, Callable[[], datetime]] = {
    # Single day terms
    "today": lambda: datetime.now(UTC),
    "yesterday": lambda: datetime.now(UTC) - timedelta(days=1),
    "tomorrow": lambda: datetime.now(UTC) + timedelta(days=1),
    # Day ranges
    "last 7 days": lambda: datetime.now(UTC) - timedelta(days=7),
    "last 30 days": lambda: datetime.now(UTC) - timedelta(days=30),
    "last 90 days": lambda: datetime.now(UTC) - timedelta(days=90),
    # Week terms
    "this week": lambda: _get_week_start(datetime.now(UTC)),
    "last week": lambda: _get_week_start(datetime.now(UTC) - timedelta(weeks=1)),
    "next week": lambda: _get_week_start(datetime.now(UTC) + timedelta(weeks=1)),
    # Month terms
    "this month": lambda: datetime.now(UTC).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    ),
    "last month": lambda: (datetime.now(UTC) - relativedelta(months=1)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    ),
    "next month": lambda: (datetime.now(UTC) + relativedelta(months=1)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    ),
    # Quarter terms
    "this quarter": lambda: _get_quarter_start(datetime.now(UTC)),
    "last quarter": lambda: _get_quarter_start(datetime.now(UTC) - relativedelta(months=3)),
    # Year terms
    "this year": lambda: datetime.now(UTC).replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    ),
    "last year": lambda: (datetime.now(UTC) - relativedelta(years=1)).replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    ),
    "next year": lambda: (datetime.now(UTC) + relativedelta(years=1)).replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    ),
}


def parse_flexible_date(date_input: str, start_of_day: bool = True) -> str:
    """Parse flexible date input and return ISO 8601 datetime string with UTC timezone.

    Supports multiple date formats with performance-optimized parsing order:
    1. Business terms (fastest, O(1) dictionary lookup)
    2. ISO 8601 dates (fast, strptime parsing)
    3. "last N days" pattern (regex + timedelta)
    4. Natural language via dateutil (slowest, fallback)

    Time-of-day handling:
    - start_of_day=True: Normalizes to 00:00:00 UTC (for start dates)
    - start_of_day=False: Normalizes to 23:59:59 UTC (for end dates)

    Supported formats:

    **Business Terms** (15+ terms):
    - Single day: "today", "yesterday", "tomorrow"
    - Day ranges: "last 7 days", "last 30 days", "last 90 days"
    - Week terms: "this week", "last week", "next week" (ISO 8601, Monday start)
    - Month terms: "this month", "last month", "next month"
    - Quarter terms: "this quarter", "last quarter" (calendar quarters: Jan/Apr/Jul/Oct 1st)
    - Year terms: "this year", "last year", "next year"

    **ISO 8601**:
    - "2024-01-01" (backward compatible, preserves existing behavior)

    **Relative Patterns**:
    - "3 days ago", "5 days ago", "10 days ago"

    **Natural Language** (via dateutil, limited scope):
    - Simple date strings that dateutil can parse
    - NOT supported: Complex phrases like "next Friday", "in 2 weeks" (future enhancement)

    Args:
        date_input: Date string in any supported format
        start_of_day: If True, normalize to 00:00:00 UTC; if False, normalize to 23:59:59 UTC

    Returns:
        ISO 8601 datetime string with UTC timezone (format: YYYY-MM-DDTHH:MM:SSZ)

    Raises:
        ToolError: If date_input cannot be parsed by any method

    Examples:
        >>> parse_flexible_date("today", start_of_day=True)
        '2024-11-06T00:00:00Z'

        >>> parse_flexible_date("today", start_of_day=False)
        '2024-11-06T23:59:59Z'

        >>> parse_flexible_date("last 30 days")
        '2024-10-07T00:00:00Z'

        >>> parse_flexible_date("this quarter")
        '2024-10-01T00:00:00Z'  # Q4 starts Oct 1

        >>> parse_flexible_date("2024-01-01")
        '2024-01-01T00:00:00Z'

        >>> parse_flexible_date("3 days ago")
        '2024-11-03T00:00:00Z'
    """
    date_input_lower = date_input.lower().strip()

    # Method 1: Business terms (O(1) lookup, fastest)
    if date_input_lower in BUSINESS_TERMS:
        parsed_date = BUSINESS_TERMS[date_input_lower]()
    else:
        # Method 2: ISO 8601 format (fast, ~1μs)
        try:
            # Parse as naive datetime, then make UTC-aware
            parsed_date = datetime.strptime(date_input, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            # Method 3a: "N days ago" pattern (regex + timedelta)
            days_ago_pattern = re.match(r"(\d+)\s+days?\s+ago", date_input_lower)
            if days_ago_pattern:
                days = int(days_ago_pattern.group(1))
                parsed_date = datetime.now(UTC) - timedelta(days=days)
            else:
                # Method 3b: "last N days" pattern (regex + timedelta)
                last_n_days_pattern = re.match(r"last\s+(\d+)\s+days?", date_input_lower)
                if last_n_days_pattern:
                    days = int(last_n_days_pattern.group(1))
                    parsed_date = datetime.now(UTC) - timedelta(days=days)
                else:
                    # Method 4: Natural language via dateutil (slowest, ~100μs)
                    try:
                        # Parse and convert to UTC-aware
                        parsed_date = dateutil_parse(date_input, fuzzy=True)
                        # If naive datetime, assume UTC
                        if parsed_date.tzinfo is None:
                            parsed_date = parsed_date.replace(tzinfo=UTC)
                        else:
                            # Convert to UTC if timezone-aware
                            parsed_date = parsed_date.astimezone(UTC)
                    except (ValueError, TypeError):
                        # All parsing methods failed
                        raise ToolError(
                            f"❌ Could not parse date: '{date_input}'\n"
                            f"ℹ️ Supported formats:\n"
                            f"   - Business terms: 'today', 'yesterday', 'last 30 days', "
                            f"'this quarter', etc.\n"
                            f"   - ISO 8601: 'YYYY-MM-DD' (e.g., '2024-01-01')\n"
                            f"   - Relative: '3 days ago', 'last 3 days'\n"
                            f"💡 Use ISO format (YYYY-MM-DD) for specific dates, "
                            f"or business terms for relative dates"
                        ) from None

    # Validate year is reasonable (1900-2100) - applies to ALL parsing methods
    # This prevents dateutil from accepting garbage like "xyz123" → year 123
    # and also catches edge cases from ISO dates or business terms
    if parsed_date.year < 1900 or parsed_date.year > 2100:
        raise ToolError(
            f"❌ Invalid date year: {parsed_date.year}\n"
            f"ℹ️ Year must be between 1900 and 2100\n"
            f"💡 Check your date input: '{date_input}'"
        )

    # Normalize time-of-day based on start_of_day parameter
    if start_of_day:
        # Start of day: 00:00:00 UTC
        normalized_date = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # End of day: 23:59:59 UTC
        normalized_date = parsed_date.replace(hour=23, minute=59, second=59, microsecond=0)

    # Return ISO 8601 datetime string with UTC timezone
    # Format: YYYY-MM-DDTHH:MM:SSZ
    return normalized_date.strftime("%Y-%m-%dT%H:%M:%SZ")
