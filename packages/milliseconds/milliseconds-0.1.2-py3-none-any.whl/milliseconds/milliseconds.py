"""
Utility class for working with POSIX timestamps in milliseconds.

This module provides methods for converting between datetime objects and millisecond
timestamps, as well as various time manipulation operations. All operations work with
POSIX time (milliseconds since Unix epoch: 1970-01-01 00:00:00 UTC).

Constants are imported from the constants module:
    constants.second: Milliseconds in one second (1,000)
    constants.minute: Milliseconds in one minute (60,000)
    constants.hour: Milliseconds in one hour (3,600,000)
    constants.day: Milliseconds in one day (86,400,000)
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from .constants import constants


class milliseconds:
    """
    A utility class for working with POSIX timestamps in milliseconds.

    All methods are static and operate on integer timestamps representing
    milliseconds since the Unix epoch (1970-01-01 00:00:00 UTC).
    """

    @staticmethod
    def milliseconds(time: datetime) -> int:
        """
        Convert a datetime object to milliseconds since Unix epoch.

        Args:
            time: A datetime object (timezone-aware or naive)

        Returns:
            Integer milliseconds since Unix epoch

        Example:
            >>> dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
            >>> milliseconds.milliseconds(dt)
            1704110400000
        """
        return int(time.timestamp() * 1000)

    @staticmethod
    def time(milliseconds: int, timezone: ZoneInfo) -> datetime:
        """
        Convert milliseconds since Unix epoch to a datetime object.

        Args:
            milliseconds: Integer milliseconds since Unix epoch
            timezone: ZoneInfo object specifying the target timezone

        Returns:
            Timezone-aware datetime object

        Example:
            >>> ms = 1704110400000
            >>> milliseconds.time(ms, ZoneInfo("UTC"))
            datetime.datetime(2024, 1, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        return datetime.fromtimestamp(milliseconds / 1000, timezone)

    @staticmethod
    def floor(milliseconds: int, factor: int = constants.hour) -> int:
        """
        Round down a timestamp to the nearest multiple of a time factor.

        This method correctly handles negative timestamps (dates before Unix epoch).
        Python's floor division automatically rounds toward negative infinity.

        Args:
            milliseconds: Timestamp in milliseconds
            factor: Time unit to floor to (default: constants.hour)

        Returns:
            Floored timestamp in milliseconds

        Example:
            >>> milliseconds.floor(1704110455000, constants.day)  # 2024-01-01 12:00:55
            1704067200000  # 2024-01-01 00:00:00
            >>> milliseconds.floor(-50000, constants.minute)  # 1969-12-31 23:59:10
            -60000  # 1969-12-31 23:59:00
        """
        return (milliseconds // factor) * factor

    @staticmethod
    def ceil(milliseconds: int, factor: int = constants.hour) -> int:
        """
        Round up a timestamp to the nearest multiple of a time factor.

        This method correctly handles negative timestamps (dates before Unix epoch).
        For negative numbers, ceiling rounds toward zero (less negative).

        Args:
            milliseconds: Timestamp in milliseconds
            factor: Time unit to ceil to (default: constants.hour)

        Returns:
            Ceiled timestamp in milliseconds

        Example:
            >>> milliseconds.ceil(1704110455000, constants.hour)  # 2024-01-01 12:00:55
            1704114000000  # 2024-01-01 13:00:00
            >>> milliseconds.ceil(-50000, constants.minute)  # 1969-12-31 23:59:10
            0  # 1970-01-01 00:00:00
        """
        # For positive: (ms + factor - 1) // factor * factor
        # For negative: use mathematical ceiling
        if milliseconds >= 0:
            return ((milliseconds + factor - 1) // factor) * factor
        else:
            # For negative numbers, floor division already rounds down (more negative)
            # So we use: if divisible, keep it; otherwise add one factor to floor result
            floored = (milliseconds // factor) * factor
            return floored if milliseconds == floored else floored + factor

    @staticmethod
    def last_second(timestamp: int) -> int:
        """
        Get the start of the previous second.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            Timestamp of the previous second boundary

        Example:
            >>> milliseconds.last_second(1704110455500)  # 12:00:55.500
            1704110454000  # 12:00:54.000
            >>> milliseconds.last_second(500)  # 1970-01-01 00:00:00.500
            0  # 1970-01-01 00:00:00.000
            >>> milliseconds.last_second(0)  # 1970-01-01 00:00:00.000
            -1000  # 1969-12-31 23:59:59.000
        """
        return milliseconds.floor(timestamp, constants.second) - constants.second

    @staticmethod
    def next_second(timestamp: int) -> int:
        """
        Get the start of the next second.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            Timestamp of the next second boundary

        Example:
            >>> milliseconds.next_second(1704110455500)  # 12:00:55.500
            1704110456000  # 12:00:56.000
        """
        return milliseconds.floor(timestamp, constants.second) + constants.second

    @staticmethod
    def last_minute(timestamp: int) -> int:
        """
        Get the start of the previous minute.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            Timestamp of the previous minute boundary

        Example:
            >>> milliseconds.last_minute(1704110455000)  # 12:00:55
            1704110400000  # 11:59:00
            >>> milliseconds.last_minute(30000)  # 1970-01-01 00:00:30
            -60000  # 1969-12-31 23:59:00
        """
        return milliseconds.floor(timestamp, constants.minute) - constants.minute

    @staticmethod
    def next_minute(timestamp: int) -> int:
        """
        Get the start of the next minute.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            Timestamp of the next minute boundary

        Example:
            >>> milliseconds.next_minute(1704110455000)  # 12:00:55
            1704110520000  # 12:01:00
        """
        return milliseconds.floor(timestamp, constants.minute) + constants.minute

    @staticmethod
    def last_hour(timestamp: int) -> int:
        """
        Get the start of the previous hour.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            Timestamp of the previous hour boundary

        Example:
            >>> milliseconds.last_hour(1704110455000)  # 12:00:55
            1704106800000  # 11:00:00
            >>> milliseconds.last_hour(1800000)  # 1970-01-01 00:30:00
            -3600000  # 1969-12-31 23:00:00
        """
        return milliseconds.floor(timestamp, constants.hour) - constants.hour

    @staticmethod
    def next_hour(timestamp: int) -> int:
        """
        Get the start of the next hour.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            Timestamp of the next hour boundary

        Example:
            >>> milliseconds.next_hour(1704110455000)  # 12:00:55
            1704114000000  # 13:00:00
        """
        return milliseconds.floor(timestamp, constants.hour) + constants.hour

    @staticmethod
    def last_day(timestamp: int) -> int:
        """
        Get the start of the previous day (UTC).

        Note: This operates on UTC day boundaries. For timezone-aware day
        boundaries, convert the timestamp to the target timezone first.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            Timestamp of the previous day boundary

        Example:
            >>> milliseconds.last_day(1704110455000)  # 2024-01-01 12:00:55 UTC
            1704067200000  # 2023-12-31 00:00:00 UTC
            >>> milliseconds.last_day(43200000)  # 1970-01-01 12:00:00 UTC
            -86400000  # 1969-12-31 00:00:00 UTC
        """
        return milliseconds.floor(timestamp, constants.day) - constants.day

    @staticmethod
    def next_day(timestamp: int) -> int:
        """
        Get the start of the next day (UTC).

        Note: This operates on UTC day boundaries. For timezone-aware day
        boundaries, convert the timestamp to the target timezone first.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            Timestamp of the next day boundary

        Example:
            >>> milliseconds.next_day(1704110455000)  # 2024-01-01 12:00:55 UTC
            1704153600000  # 2024-01-02 00:00:00 UTC
        """
        return milliseconds.floor(timestamp, constants.day) + constants.day

    @staticmethod
    def is_valid_second(timestamp: int) -> bool:
        """
        Check if timestamp is aligned to a second boundary.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            True if timestamp has no millisecond component

        Example:
            >>> milliseconds.is_valid_second(1704110455000)
            True
            >>> milliseconds.is_valid_second(1704110455500)
            False
        """
        return timestamp % constants.second == 0

    @staticmethod
    def is_valid_minute(timestamp: int) -> bool:
        """
        Check if timestamp is aligned to a minute boundary.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            True if timestamp has no second or millisecond component

        Example:
            >>> milliseconds.is_valid_minute(1704110400000)
            True
            >>> milliseconds.is_valid_minute(1704110455000)
            False
        """
        return timestamp % constants.minute == 0

    @staticmethod
    def is_valid_hour(timestamp: int) -> bool:
        """
        Check if timestamp is aligned to an hour boundary.

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            True if timestamp has no minute, second, or millisecond component

        Example:
            >>> milliseconds.is_valid_hour(1704110400000)
            True
            >>> milliseconds.is_valid_hour(1704110455000)
            False
        """
        return timestamp % constants.hour == 0

    @staticmethod
    def is_valid_day(timestamp: int) -> bool:
        """
        Check if timestamp is aligned to a day boundary (UTC).

        Args:
            timestamp: Timestamp in milliseconds

        Returns:
            True if timestamp represents midnight UTC

        Example:
            >>> milliseconds.is_valid_day(1704067200000)  # 2024-01-01 00:00:00 UTC
            True
            >>> milliseconds.is_valid_day(1704110455000)  # 2024-01-01 12:00:55 UTC
            False
        """
        return timestamp % constants.day == 0

    @staticmethod
    def increment_second(timestamp: int, n: float = 1) -> int:
        """
        Add seconds to a timestamp.

        Args:
            timestamp: Timestamp in milliseconds
            n: Number of seconds to add (can be fractional)

        Returns:
            New timestamp in milliseconds

        Example:
            >>> milliseconds.increment_second(1704110455000, 5)
            1704110460000
            >>> milliseconds.increment_second(1704110455000, 0.5)
            1704110455500
        """
        return timestamp + int(constants.second * n)

    @staticmethod
    def decrement_second(timestamp: int, n: float = 1) -> int:
        """
        Subtract seconds from a timestamp.

        Args:
            timestamp: Timestamp in milliseconds
            n: Number of seconds to subtract (can be fractional)

        Returns:
            New timestamp in milliseconds

        Example:
            >>> milliseconds.decrement_second(1704110455000, 5)
            1704110450000
            >>> milliseconds.decrement_second(500, 1)  # 1970-01-01 00:00:00.500
            -500  # 1969-12-31 23:59:59.500
        """
        return timestamp - int(constants.second * n)

    @staticmethod
    def increment_minute(timestamp: int, n: float = 1) -> int:
        """
        Add minutes to a timestamp.

        Args:
            timestamp: Timestamp in milliseconds
            n: Number of minutes to add (can be fractional)

        Returns:
            New timestamp in milliseconds

        Example:
            >>> milliseconds.increment_minute(1704110400000, 30)
            1704112200000
        """
        return timestamp + int(constants.minute * n)

    @staticmethod
    def decrement_minute(timestamp: int, n: float = 1) -> int:
        """
        Subtract minutes from a timestamp.

        Args:
            timestamp: Timestamp in milliseconds
            n: Number of minutes to subtract (can be fractional)

        Returns:
            New timestamp in milliseconds

        Example:
            >>> milliseconds.decrement_minute(1704110400000, 10)
            1704109800000
            >>> milliseconds.decrement_minute(30000, 1)  # 1970-01-01 00:00:30
            -30000  # 1969-12-31 23:59:30
        """
        return timestamp - int(constants.minute * n)

    @staticmethod
    def increment_hour(timestamp: int, n: float = 1) -> int:
        """
        Add hours to a timestamp.

        Args:
            timestamp: Timestamp in milliseconds
            n: Number of hours to add (can be fractional)

        Returns:
            New timestamp in milliseconds

        Example:
            >>> milliseconds.increment_hour(1704110400000, 2)
            1704117600000
        """
        return timestamp + int(constants.hour * n)

    @staticmethod
    def decrement_hour(timestamp: int, n: float = 1) -> int:
        """
        Subtract hours from a timestamp.

        Args:
            timestamp: Timestamp in milliseconds
            n: Number of hours to subtract (can be fractional)

        Returns:
            New timestamp in milliseconds

        Example:
            >>> milliseconds.decrement_hour(1704110400000, 3)
            1704099600000
            >>> milliseconds.decrement_hour(1800000, 1)  # 1970-01-01 00:30:00
            -1800000  # 1969-12-31 23:30:00
        """
        return timestamp - int(constants.hour * n)

    @staticmethod
    def increment_day(timestamp: int, n: float = 1) -> int:
        """
        Add days to a timestamp.

        Args:
            timestamp: Timestamp in milliseconds
            n: Number of days to add (can be fractional)

        Returns:
            New timestamp in milliseconds

        Example:
            >>> milliseconds.increment_day(1704067200000, 1)
            1704153600000
        """
        return timestamp + int(constants.day * n)

    @staticmethod
    def decrement_day(timestamp: int, n: float = 1) -> int:
        """
        Subtract days from a timestamp.

        Args:
            timestamp: Timestamp in milliseconds
            n: Number of days to subtract (can be fractional)

        Returns:
            New timestamp in milliseconds

        Example:
            >>> milliseconds.decrement_day(1704067200000, 1)
            1703980800000
            >>> milliseconds.decrement_day(43200000, 1)  # 1970-01-01 12:00:00
            -43200000  # 1969-12-31 12:00:00
        """
        return timestamp - int(constants.day * n)

    @staticmethod
    def is_same_second(ts1: int, ts2: int) -> bool:
        """
        Check if two timestamps fall within the same second.

        Args:
            ts1: First timestamp in milliseconds
            ts2: Second timestamp in milliseconds

        Returns:
            True if both timestamps are in the same second

        Example:
            >>> milliseconds.is_same_second(1704110455100, 1704110455900)
            True
            >>> milliseconds.is_same_second(1704110455900, 1704110456100)
            False
        """
        return milliseconds.floor(ts1, constants.second) == milliseconds.floor(
            ts2, constants.second
        )

    @staticmethod
    def is_same_minute(ts1: int, ts2: int) -> bool:
        """
        Check if two timestamps fall within the same minute.

        Args:
            ts1: First timestamp in milliseconds
            ts2: Second timestamp in milliseconds

        Returns:
            True if both timestamps are in the same minute

        Example:
            >>> milliseconds.is_same_minute(1704110400000, 1704110459000)
            True
            >>> milliseconds.is_same_minute(1704110459000, 1704110460000)
            False
        """
        return milliseconds.floor(ts1, constants.minute) == milliseconds.floor(
            ts2, constants.minute
        )

    @staticmethod
    def is_same_hour(ts1: int, ts2: int) -> bool:
        """
        Check if two timestamps fall within the same hour.

        Args:
            ts1: First timestamp in milliseconds
            ts2: Second timestamp in milliseconds

        Returns:
            True if both timestamps are in the same hour

        Example:
            >>> milliseconds.is_same_hour(1704110400000, 1704113999000)
            True
            >>> milliseconds.is_same_hour(1704113999000, 1704114000000)
            False
        """
        return milliseconds.floor(ts1, constants.hour) == milliseconds.floor(
            ts2, constants.hour
        )

    @staticmethod
    def is_same_day(ts1: int, ts2: int) -> bool:
        """
        Check if two timestamps fall within the same day (UTC).

        Note: This compares UTC day boundaries. For timezone-aware comparisons,
        convert timestamps to the target timezone before comparison.

        Args:
            ts1: First timestamp in milliseconds
            ts2: Second timestamp in milliseconds

        Returns:
            True if both timestamps are on the same UTC day

        Example:
            >>> milliseconds.is_same_day(1704067200000, 1704153599000)
            True
            >>> milliseconds.is_same_day(1704153599000, 1704153600000)
            False
        """
        return milliseconds.floor(ts1, constants.day) == milliseconds.floor(
            ts2, constants.day
        )
