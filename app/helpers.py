from datetime import datetime


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
