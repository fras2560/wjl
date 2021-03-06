# -*- coding: utf-8 -*-
"""Holds general helper functions."""
from datetime import datetime, timedelta


def is_date_between_range(date: datetime, start_range: datetime,
                          end_range: datetime) -> bool:
    """Is the given date between the start and end range.

    Args:
        date (datetime): the date to check
        start_range (datetime): the start of the range
        end_range (datetime): the end of the range

    Returns:
        bool: true if date is between range otherwise false
    """
    return date >= start_range and date <= end_range


def tomorrow_date() -> datetime:
    """Get tomorrows date.

    Returns:
        datetime:tomorrow
    """
    return datetime.today() + timedelta(days=1)
