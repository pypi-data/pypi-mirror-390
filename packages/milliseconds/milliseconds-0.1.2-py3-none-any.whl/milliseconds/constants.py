"""
Time unit constants in milliseconds.

This module provides an IntEnum of time unit constants for working with
millisecond timestamps. All values represent the number of milliseconds
in each respective time unit.
"""

from enum import IntEnum


class constants(IntEnum):
    """
    Time unit constants in milliseconds.

    This IntEnum provides standard time unit conversions to milliseconds
    for use with POSIX timestamp operations.

    Attributes:
        second: Milliseconds in one second (1,000)
        minute: Milliseconds in one minute (60,000)
        hour: Milliseconds in one hour (3,600,000)
        day: Milliseconds in one day (86,400,000)

    Example:
        >>> constants.second
        1000
        >>> constants.hour * 2
        7200000
        >>> timestamp = 1704110400000
        >>> timestamp % constants.day == 0  # Check if midnight
        False
    """

    """Milliseconds in one second (1,000)"""
    second = 1_000

    """Milliseconds in one minute (60,000)"""
    minute = 60_000

    """Milliseconds in one hour (3,600,000)"""
    hour = 3_600_000

    """Milliseconds in one day (86,400,000)"""
    day = 86_400_000
