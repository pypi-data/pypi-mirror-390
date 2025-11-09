# milliseconds

[![PyPI - Version](https://img.shields.io/pypi/v/milliseconds.svg)](https://pypi.org/project/milliseconds)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/milliseconds.svg)](https://pypi.org/project/milliseconds)
[![CI](https://github.com/traverne/milliseconds/workflows/CI/badge.svg)](https://github.com/traverne/milliseconds/actions)

A lightweight, POSIX-compliant utility library for working with timestamps in milliseconds.

-----

## Features

- **Convert between datetime and milliseconds** - Easy conversion to/from Python datetime objects
- **Floor and ceil operations** - Round timestamps to specific time boundaries (second, minute, hour, day)
- **Boundary navigation** - Jump to next/previous time boundaries
- **Validation** - Check if timestamps align to specific time units
- **Arithmetic operations** - Increment/decrement by seconds, minutes, hours, or days
- **Comparison utilities** - Check if timestamps fall within the same time period
- **Full POSIX compliance** - Supports negative timestamps (dates before 1970-01-01)
- **Zero dependencies** - Only uses Python standard library
- **Type hints** - Fully typed for better IDE support

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [Basic Conversion](#basic-conversion)
  - [Floor and Ceil Operations](#floor-and-ceil-operations)
  - [Boundary Navigation](#boundary-navigation)
  - [Time Arithmetic](#time-arithmetic)
  - [Validation](#validation)
  - [Comparison](#comparison)
  - [Working with Negative Timestamps](#working-with-negative-timestamps)
- [API Reference](#api-reference)
- [License](#license)

## Installation

```console
pip install milliseconds
```

## Quick Start

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from milliseconds import milliseconds, constants

# Convert datetime to milliseconds
dt = datetime(2024, 1, 1, 12, 30, 45, tzinfo=ZoneInfo("UTC"))
ms = milliseconds.milliseconds(dt)
print(ms)  # 1704113445000

# Convert back to datetime
dt_back = milliseconds.time(ms, ZoneInfo("UTC"))
print(dt_back)  # 2024-01-01 12:30:45+00:00

# Floor to nearest hour
floored = milliseconds.floor(ms, constants.hour)
print(milliseconds.time(floored, ZoneInfo("UTC")))  # 2024-01-01 12:00:00+00:00

# Get next day boundary
next_day = milliseconds.next_day(ms)
print(milliseconds.time(next_day, ZoneInfo("UTC")))  # 2024-01-02 00:00:00+00:00
```

## Usage Examples

### Basic Conversion

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from milliseconds import milliseconds

# DateTime to milliseconds
dt = datetime(2024, 6, 15, 14, 30, 0, tzinfo=ZoneInfo("UTC"))
ms = milliseconds.milliseconds(dt)
print(ms)  # 1718460600000

# Milliseconds to datetime
dt_back = milliseconds.time(ms, ZoneInfo("America/New_York"))
print(dt_back)  # 2024-06-15 10:30:00-04:00 (EDT)
```

### Floor and Ceil Operations

```python
from milliseconds import milliseconds, constants

timestamp = 1704113445789  # 2024-01-01 12:30:45.789

# Floor operations (round down)
print(milliseconds.floor(timestamp, constants.second))  # 1704113445000 (12:30:45.000)
print(milliseconds.floor(timestamp, constants.minute))  # 1704113400000 (12:30:00.000)
print(milliseconds.floor(timestamp, constants.hour))    # 1704110400000 (12:00:00.000)
print(milliseconds.floor(timestamp, constants.day))     # 1704067200000 (00:00:00.000)

# Ceil operations (round up)
print(milliseconds.ceil(timestamp, constants.second))   # 1704113446000 (12:30:46.000)
print(milliseconds.ceil(timestamp, constants.minute))   # 1704113460000 (12:31:00.000)
print(milliseconds.ceil(timestamp, constants.hour))     # 1704114000000 (13:00:00.000)
```

### Boundary Navigation

```python
from milliseconds import milliseconds

timestamp = 1704113445789  # 2024-01-01 12:30:45.789

# Navigate to previous boundaries
print(milliseconds.last_second(timestamp))  # Previous second: 12:30:44.000
print(milliseconds.last_minute(timestamp))  # Previous minute: 12:29:00.000
print(milliseconds.last_hour(timestamp))    # Previous hour: 11:00:00.000
print(milliseconds.last_day(timestamp))     # Previous day: 2023-12-31 00:00:00

# Navigate to next boundaries
print(milliseconds.next_second(timestamp))  # Next second: 12:30:46.000
print(milliseconds.next_minute(timestamp))  # Next minute: 12:31:00.000
print(milliseconds.next_hour(timestamp))    # Next hour: 13:00:00.000
print(milliseconds.next_day(timestamp))     # Next day: 2024-01-02 00:00:00
```

### Time Arithmetic

```python
from milliseconds import milliseconds

timestamp = 1704067200000  # 2024-01-01 00:00:00

# Increment operations
plus_30_sec = milliseconds.increment_second(timestamp, 30)
plus_15_min = milliseconds.increment_minute(timestamp, 15)
plus_6_hours = milliseconds.increment_hour(timestamp, 6)
plus_7_days = milliseconds.increment_day(timestamp, 7)

# Decrement operations
minus_30_sec = milliseconds.decrement_second(timestamp, 30)
minus_15_min = milliseconds.decrement_minute(timestamp, 15)
minus_6_hours = milliseconds.decrement_hour(timestamp, 6)
minus_7_days = milliseconds.decrement_day(timestamp, 7)

# Fractional values are supported
plus_half_hour = milliseconds.increment_hour(timestamp, 0.5)
minus_quarter_day = milliseconds.decrement_day(timestamp, 0.25)
```

### Validation

```python
from milliseconds import milliseconds

# Check if timestamp aligns to boundaries
timestamp = 1704110400000  # 2024-01-01 12:00:00.000

print(milliseconds.is_valid_second(timestamp))  # True (no milliseconds)
print(milliseconds.is_valid_minute(timestamp))  # True (no seconds)
print(milliseconds.is_valid_hour(timestamp))    # True (no minutes)
print(milliseconds.is_valid_day(timestamp))     # False (not midnight UTC)

timestamp_with_ms = 1704110400500  # 12:00:00.500
print(milliseconds.is_valid_second(timestamp_with_ms))  # False (has milliseconds)
```

### Comparison

```python
from milliseconds import milliseconds

ts1 = 1704110455100  # 2024-01-01 12:00:55.100
ts2 = 1704110455900  # 2024-01-01 12:00:55.900
ts3 = 1704110460000  # 2024-01-01 12:01:00.000

# Check if timestamps are in the same period
print(milliseconds.is_same_second(ts1, ts2))  # True (both in second :55)
print(milliseconds.is_same_second(ts2, ts3))  # False (different seconds)

print(milliseconds.is_same_minute(ts1, ts3))  # True (both in minute 12:00)
print(milliseconds.is_same_hour(ts1, ts3))    # True (both in hour 12:00)
print(milliseconds.is_same_day(ts1, ts3))     # True (both on 2024-01-01)
```

### Working with Negative Timestamps

POSIX timestamps support dates before the Unix epoch (1970-01-01). This library handles them correctly:

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from milliseconds import milliseconds

# Create a date before 1970
dt = datetime(1969, 12, 31, 23, 0, 0, tzinfo=ZoneInfo("UTC"))
ms = milliseconds.milliseconds(dt)
print(ms)  # -3600000

# Operations work correctly
last_hour = milliseconds.last_hour(ms)
print(milliseconds.time(last_hour, ZoneInfo("UTC")))  # 1969-12-31 22:00:00

# Arithmetic works naturally
earlier = milliseconds.decrement_day(ms, 1)
print(milliseconds.time(earlier, ZoneInfo("UTC")))  # 1969-12-30 23:00:00
```

## API Reference

### Constants

The `constants` IntEnum provides time unit values in milliseconds:

```python
from milliseconds import constants

constants.second  # 1_000 - Milliseconds in one second
constants.minute  # 60_000 - Milliseconds in one minute
constants.hour    # 3_600_000 - Milliseconds in one hour
constants.day     # 86_400_000 - Milliseconds in one day
```

### Conversion Methods

- `milliseconds(time: datetime) -> int` - Convert datetime to milliseconds
- `time(milliseconds: int, timezone: ZoneInfo) -> datetime` - Convert milliseconds to datetime

### Rounding Methods

- `floor(milliseconds: int, factor: int = constants.hour) -> int` - Round down to nearest factor
- `ceil(milliseconds: int, factor: int = constants.hour) -> int` - Round up to nearest factor

### Boundary Navigation

- `last_second(timestamp: int) -> int` - Get start of previous second
- `next_second(timestamp: int) -> int` - Get start of next second
- `last_minute(timestamp: int) -> int` - Get start of previous minute
- `next_minute(timestamp: int) -> int` - Get start of next minute
- `last_hour(timestamp: int) -> int` - Get start of previous hour
- `next_hour(timestamp: int) -> int` - Get start of next hour
- `last_day(timestamp: int) -> int` - Get start of previous day (UTC)
- `next_day(timestamp: int) -> int` - Get start of next day (UTC)

### Validation Methods

- `is_valid_second(timestamp: int) -> bool` - Check if aligned to second boundary
- `is_valid_minute(timestamp: int) -> bool` - Check if aligned to minute boundary
- `is_valid_hour(timestamp: int) -> bool` - Check if aligned to hour boundary
- `is_valid_day(timestamp: int) -> bool` - Check if aligned to day boundary

### Arithmetic Methods

- `increment_second(timestamp: int, n: float = 1) -> int` - Add seconds
- `decrement_second(timestamp: int, n: float = 1) -> int` - Subtract seconds
- `increment_minute(timestamp: int, n: float = 1) -> int` - Add minutes
- `decrement_minute(timestamp: int, n: float = 1) -> int` - Subtract minutes
- `increment_hour(timestamp: int, n: float = 1) -> int` - Add hours
- `decrement_hour(timestamp: int, n: float = 1) -> int` - Subtract hours
- `increment_day(timestamp: int, n: float = 1) -> int` - Add days
- `decrement_day(timestamp: int, n: float = 1) -> int` - Subtract days

### Comparison Methods

- `is_same_second(ts1: int, ts2: int) -> bool` - Check if in same second
- `is_same_minute(ts1: int, ts2: int) -> bool` - Check if in same minute
- `is_same_hour(ts1: int, ts2: int) -> bool` - Check if in same hour
- `is_same_day(ts1: int, ts2: int) -> bool` - Check if in same day (UTC)

## License

`milliseconds` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
