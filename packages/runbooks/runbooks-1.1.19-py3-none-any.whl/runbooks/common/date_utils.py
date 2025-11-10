#!/usr/bin/env python3
"""
Dynamic Date Utilities for Runbooks Platform

Replaces hardcoded 2024 dates with dynamic date generation following manager's
"No hardcoded values" requirement. Supports current month/year calculations
for all test data and AWS API time period generation.

Strategic Alignment: "Do one thing and do it well" - Focused date utility
KISS Principle: Simple, reusable date functions for all modules
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple


def get_current_year() -> int:
    """Get current year dynamically."""
    return datetime.now().year


def get_current_month_period() -> Dict[str, str]:
    """
    Generate current month's start and end dates for AWS API calls.

    Returns:
        Dict with 'Start' and 'End' keys in YYYY-MM-DD format
    """
    now = datetime.now()
    start_date = now.replace(day=1).strftime("%Y-%m-%d")

    # Get last day of current month
    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)

    end_date = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")

    return {"Start": start_date, "End": end_date}


def get_previous_month_period() -> Dict[str, str]:
    """
    Generate previous month's start and end dates for AWS API calls.

    Returns:
        Dict with 'Start' and 'End' keys in YYYY-MM-DD format
    """
    now = datetime.now()

    # Get first day of previous month
    if now.month == 1:
        prev_month = now.replace(year=now.year - 1, month=12, day=1)
    else:
        prev_month = now.replace(month=now.month - 1, day=1)

    start_date = prev_month.strftime("%Y-%m-%d")

    # Get last day of previous month
    end_date = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")

    return {"Start": start_date, "End": end_date}


def get_test_date_period(days_back: int = 30) -> Dict[str, str]:
    """
    Generate test date periods for consistent test data.

    Args:
        days_back: Number of days back from today for start date

    Returns:
        Dict with 'Start' and 'End' keys in YYYY-MM-DD format
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    return {"Start": start_date, "End": end_date}


def get_aws_cli_example_period() -> Tuple[str, str]:
    """
    Generate example date period for AWS CLI documentation.
    Uses yesterday and today to ensure valid time range.

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    return (yesterday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))


def get_collection_timestamp() -> str:
    """
    Generate collection timestamp for test data.

    Returns:
        ISO format timestamp string
    """
    return datetime.now().isoformat()
