"""
Unit tests for the milliseconds module.

Run with: pytest tests/test_milliseconds.py
Or with hatch: hatch run test
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from milliseconds import milliseconds, constants


class TestConstants:
    """Test module constants."""

    def test_constants_values(self):
        assert constants.second == 1_000
        assert constants.minute == 60_000
        assert constants.hour == 3_600_000
        assert constants.day == 86_400_000


class TestConversion:
    """Test datetime to millisecond conversions."""

    def test_milliseconds_from_datetime(self):
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        result = milliseconds.milliseconds(dt)
        assert result == 1704110400000

    def test_milliseconds_from_datetime_with_microseconds(self):
        dt = datetime(2024, 1, 1, 12, 0, 0, 500000, tzinfo=ZoneInfo("UTC"))
        result = milliseconds.milliseconds(dt)
        assert result == 1704110400500

    def test_time_to_datetime(self):
        ms = 1704110400000
        result = milliseconds.time(ms, ZoneInfo("UTC"))
        expected = datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        assert result == expected

    def test_time_to_datetime_with_milliseconds(self):
        ms = 1704110400500
        result = milliseconds.time(ms, ZoneInfo("UTC"))
        assert result.microsecond == 500000

    def test_conversion_roundtrip(self):
        dt = datetime(2024, 6, 15, 14, 30, 45, 123000, tzinfo=ZoneInfo("UTC"))
        ms = milliseconds.milliseconds(dt)
        result = milliseconds.time(ms, ZoneInfo("UTC"))
        assert result == dt

    def test_negative_timestamp_conversion(self):
        # December 31, 1969, 23:00:00 UTC
        ms = -3600000
        result = milliseconds.time(ms, ZoneInfo("UTC"))
        assert result.year == 1969
        assert result.month == 12
        assert result.day == 31
        assert result.hour == 23


class TestFloorCeil:
    """Test floor and ceil operations."""

    def test_floor_to_hour(self):
        # 2024-01-01 12:34:56.789
        ms = 1704112496789
        result = milliseconds.floor(ms, constants.hour)
        assert result == 1704110400000  # 2024-01-01 12:00:00

    def test_floor_to_day(self):
        ms = 1704112496789
        result = milliseconds.floor(ms, constants.day)
        assert result == 1704067200000  # 2024-01-01 00:00:00

    def test_floor_already_aligned(self):
        ms = 1704110400000  # Already at hour boundary
        result = milliseconds.floor(ms, constants.hour)
        assert result == ms

    def test_floor_negative_timestamp(self):
        ms = -50000  # 1969-12-31 23:59:10
        result = milliseconds.floor(ms, constants.minute)
        assert result == -60000  # 1969-12-31 23:59:00

    def test_ceil_to_hour(self):
        ms = 1704110455000  # 2024-01-01 12:00:55
        result = milliseconds.ceil(ms, constants.hour)
        assert result == 1704114000000  # 2024-01-01 13:00:00

    def test_ceil_already_aligned(self):
        ms = 1704110400000  # Already at hour boundary
        result = milliseconds.ceil(ms, constants.hour)
        assert result == ms

    def test_ceil_negative_timestamp(self):
        ms = -50000  # 1969-12-31 23:59:10
        result = milliseconds.ceil(ms, constants.minute)
        assert result == 0  # 1970-01-01 00:00:00

    def test_ceil_negative_aligned(self):
        ms = -60000  # 1969-12-31 23:59:00 (already aligned)
        result = milliseconds.ceil(ms, constants.minute)
        assert result == -60000


class TestLastNext:
    """Test last_* and next_* boundary methods."""

    def test_last_second(self):
        ms = 1704110455500  # 12:00:55.500
        result = milliseconds.last_second(ms)
        assert result == 1704110454000  # 12:00:54.000

    def test_next_second(self):
        ms = 1704110455500  # 12:00:55.500
        result = milliseconds.next_second(ms)
        assert result == 1704110456000  # 12:00:56.000

    def test_last_minute(self):
        ms = 1704110455000  # 12:00:55
        result = milliseconds.last_minute(ms)
        assert result == 1704110340000  # 11:59:00

    def test_next_minute(self):
        ms = 1704110455000  # 12:00:55
        result = milliseconds.next_minute(ms)
        assert result == 1704110460000  # 12:01:00

    def test_last_hour(self):
        ms = 1704110455000  # 12:00:55
        result = milliseconds.last_hour(ms)
        assert result == 1704106800000  # 11:00:00

    def test_next_hour(self):
        ms = 1704110455000  # 12:00:55
        result = milliseconds.next_hour(ms)
        assert result == 1704114000000  # 13:00:00

    def test_last_day(self):
        ms = 1704110455000  # 2024-01-01 12:00:55
        result = milliseconds.last_day(ms)
        assert result == 1703980800000  # 2023-12-31 00:00:00

    def test_next_day(self):
        ms = 1704110455000  # 2024-01-01 12:00:55
        result = milliseconds.next_day(ms)
        assert result == 1704153600000  # 2024-01-02 00:00:00

    def test_last_second_negative_result(self):
        ms = 500  # 1970-01-01 00:00:00.500
        result = milliseconds.last_second(ms)
        assert result == -1000  # 1969-12-31 23:59:59.000

    def test_last_day_negative_result(self):
        ms = 43200000  # 1970-01-01 12:00:00
        result = milliseconds.last_day(ms)
        assert result == -86400000  # 1969-12-31 00:00:00


class TestValidation:
    """Test is_valid_* alignment checking methods."""

    def test_is_valid_second_true(self):
        assert milliseconds.is_valid_second(1704110455000) is True

    def test_is_valid_second_false(self):
        assert milliseconds.is_valid_second(1704110455500) is False

    def test_is_valid_minute_true(self):
        assert milliseconds.is_valid_minute(1704110400000) is True

    def test_is_valid_minute_false(self):
        assert milliseconds.is_valid_minute(1704110455000) is False

    def test_is_valid_hour_true(self):
        assert milliseconds.is_valid_hour(1704110400000) is True

    def test_is_valid_hour_false(self):
        assert milliseconds.is_valid_hour(1704110455000) is False

    def test_is_valid_day_true(self):
        assert milliseconds.is_valid_day(1704067200000) is True

    def test_is_valid_day_false(self):
        assert milliseconds.is_valid_day(1704110455000) is False

    def test_is_valid_with_negative_timestamps(self):
        assert milliseconds.is_valid_hour(-3600000) is True
        assert milliseconds.is_valid_minute(-60000) is True


class TestIncrement:
    """Test increment_* methods."""

    def test_increment_second(self):
        ms = 1704110455000
        result = milliseconds.increment_second(ms, 5)
        assert result == 1704110460000

    def test_increment_second_fractional(self):
        ms = 1704110455000
        result = milliseconds.increment_second(ms, 0.5)
        assert result == 1704110455500

    def test_increment_minute(self):
        ms = 1704110400000
        result = milliseconds.increment_minute(ms, 30)
        assert result == 1704112200000

    def test_increment_hour(self):
        ms = 1704110400000
        result = milliseconds.increment_hour(ms, 2)
        assert result == 1704117600000

    def test_increment_day(self):
        ms = 1704067200000
        result = milliseconds.increment_day(ms, 1)
        assert result == 1704153600000

    def test_increment_from_negative(self):
        ms = -86400000  # 1969-12-31 00:00:00
        result = milliseconds.increment_day(ms, 1)
        assert result == 0  # 1970-01-01 00:00:00


class TestDecrement:
    """Test decrement_* methods."""

    def test_decrement_second(self):
        ms = 1704110455000
        result = milliseconds.decrement_second(ms, 5)
        assert result == 1704110450000

    def test_decrement_second_fractional(self):
        ms = 1704110455000
        result = milliseconds.decrement_second(ms, 0.5)
        assert result == 1704110454500

    def test_decrement_minute(self):
        ms = 1704110400000
        result = milliseconds.decrement_minute(ms, 10)
        assert result == 1704109800000

    def test_decrement_hour(self):
        ms = 1704110400000
        result = milliseconds.decrement_hour(ms, 3)
        assert result == 1704099600000

    def test_decrement_day(self):
        ms = 1704067200000
        result = milliseconds.decrement_day(ms, 1)
        assert result == 1703980800000

    def test_decrement_to_negative(self):
        ms = 500  # 1970-01-01 00:00:00.500
        result = milliseconds.decrement_second(ms, 1)
        assert result == -500  # 1969-12-31 23:59:59.500

    def test_decrement_day_to_negative(self):
        ms = 43200000  # 1970-01-01 12:00:00
        result = milliseconds.decrement_day(ms, 1)
        assert result == -43200000  # 1969-12-31 12:00:00


class TestComparison:
    """Test is_same_* comparison methods."""

    def test_is_same_second_true(self):
        ts1 = 1704110455100
        ts2 = 1704110455900
        assert milliseconds.is_same_second(ts1, ts2) is True

    def test_is_same_second_false(self):
        ts1 = 1704110455900
        ts2 = 1704110456100
        assert milliseconds.is_same_second(ts1, ts2) is False

    def test_is_same_minute_true(self):
        ts1 = 1704110400000
        ts2 = 1704110459000
        assert milliseconds.is_same_minute(ts1, ts2) is True

    def test_is_same_minute_false(self):
        ts1 = 1704110459000
        ts2 = 1704110460000
        assert milliseconds.is_same_minute(ts1, ts2) is False

    def test_is_same_hour_true(self):
        ts1 = 1704110400000
        ts2 = 1704113999000
        assert milliseconds.is_same_hour(ts1, ts2) is True

    def test_is_same_hour_false(self):
        ts1 = 1704113999000
        ts2 = 1704114000000
        assert milliseconds.is_same_hour(ts1, ts2) is False

    def test_is_same_day_true(self):
        ts1 = 1704067200000  # 2024-01-01 00:00:00
        ts2 = 1704153599000  # 2024-01-01 23:59:59
        assert milliseconds.is_same_day(ts1, ts2) is True

    def test_is_same_day_false(self):
        ts1 = 1704153599000  # 2024-01-01 23:59:59
        ts2 = 1704153600000  # 2024-01-02 00:00:00
        assert milliseconds.is_same_day(ts1, ts2) is False

    def test_is_same_with_negative_timestamps(self):
        ts1 = -3600000  # 1969-12-31 23:00:00
        ts2 = -1800000  # 1969-12-31 23:30:00
        assert milliseconds.is_same_hour(ts1, ts2) is True


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_epoch_zero(self):
        assert milliseconds.floor(0, constants.hour) == 0
        assert milliseconds.ceil(0, constants.hour) == 0
        assert milliseconds.is_valid_second(0) is True

    def test_very_large_timestamp(self):
        # Year 2100
        ms = 4102444800000
        result = milliseconds.increment_day(ms, 1)
        assert result == ms + constants.day

    def test_very_negative_timestamp(self):
        # Year 1900
        ms = -2208988800000
        result = milliseconds.decrement_day(ms, 1)
        assert result == ms - constants.day

    def test_timezone_conversion(self):
        ms = 1704110400000
        utc_dt = milliseconds.time(ms, ZoneInfo("UTC"))
        est_dt = milliseconds.time(ms, ZoneInfo("America/New_York"))

        # Same timestamp, different timezones
        assert utc_dt.hour == 12
        assert est_dt.hour == 7  # EST is UTC-5

    def test_fractional_operations(self):
        ms = 1704110400000
        result = milliseconds.increment_second(ms, 1.5)
        assert result == 1704110401500

        result = milliseconds.decrement_hour(ms, 0.25)
        assert result == ms - (constants.hour // 4)
