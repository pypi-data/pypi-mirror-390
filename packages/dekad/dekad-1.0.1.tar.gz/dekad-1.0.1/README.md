# Dekad

A Python package for handling dekads (10-day periods) commonly used in agrometeorology and climate science.

## Overview

A dekad is a period of 10 days used in meteorological and agricultural applications. Each month is divided into three dekads:

- **Dekad 1**: Days 1-10
- **Dekad 2**: Days 11-20
- **Dekad 3**: Days 21 to the end of the month

Each year consists of 36 dekads (12 months x 3 dekads).

This package provides a `Dekad` class for working with dekad-based temporal data, including conversion to and from dates, arithmetic operations, and iteration.

## Installation

Install using pip:

```bash
pip install dekad
```

## Quick Start

```python
from dekad import Dekad, dekad_range
import datetime

# Create a Dekad from a date
date = datetime.date(2024, 5, 15)
d = Dekad.from_date(date)
print(d)  # 2024-D14

# Create a Dekad directly
d = Dekad(2024, 15)  # 15th dekad of 2024

# Create from year, month, and dekad of month
d = Dekad.from_ymd(2024, 5, 3)  # 3rd dekad of May 2024

# Convert to dates
print(d.first_date())  # 2024-05-21
print(d.last_date())   # 2024-05-31

# Access properties
print(d.year)           # 2024
print(d.dekad_of_year)  # 15
print(d.month)          # 5
print(d.dekad_of_month) # 3

# Arithmetic operations
d2 = d + 5              # Add 5 dekads
d3 = d - 3              # Subtract 3 dekads
diff = d2 - d3          # Difference in dekads (returns 8)

# Iterate over dekads
for dekad in dekad_range(Dekad(2024, 1), Dekad(2024, 4)):
    print(dekad)
# Output:
# 2024-D01
# 2024-D02
# 2024-D03
```

## API Reference

### Dekad Class

#### Constructors

- `Dekad(year: int, dekad_of_year: int)` - Create a Dekad from year and dekad number (1-36)
- `Dekad.from_date(date: datetime.date)` - Create a Dekad from a date
- `Dekad.from_ymd(year: int, month: int, dekad_of_month: int)` - Create from year, month, and dekad of month (1-3)

#### Properties

- `year: int` - The year
- `dekad_of_year: int` - Dekad number within the year (1-36)
- `month: int` - The month (1-12)
- `dekad_of_month: int` - Dekad number within the month (1-3)

#### Methods

- `first_date() -> datetime.date` - Get the first date of the dekad
- `last_date() -> datetime.date` - Get the last date of the dekad

#### Arithmetic Operations

- `dekad + int` - Add dekads
- `dekad - int` - Subtract dekads
- `dekad - dekad` - Calculate difference in dekads (returns int)
- `int + dekad` - Add dekads (commutative)

#### Comparison Operations

Supports all comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`

#### Collections Support

Dekad objects are hashable and can be used in sets and as dictionary keys.

### Utility Functions

- `dekad_range(start: Dekad, end: Dekad, step: int = 1)` - Generate a range of Dekad objects, similar to Python's `range()` function. The range is inclusive of start but exclusive of end.

## Examples

### Working with Leap Years

```python
from dekad import Dekad

# February 2024 (leap year)
feb_dekad3_2024 = Dekad.from_ymd(2024, 2, 3)
print(feb_dekad3_2024.last_date())  # 2024-02-29

# February 2023 (non-leap year)
feb_dekad3_2023 = Dekad.from_ymd(2023, 2, 3)
print(feb_dekad3_2023.last_date())  # 2023-02-28
```

### Iterating Over a Year

```python
from dekad import Dekad, dekad_range

# Iterate through all dekads in 2024
for dekad in dekad_range(Dekad(2024, 1), Dekad(2025, 1)):
    print(f"{dekad}: {dekad.first_date()} to {dekad.last_date()}")
```

### Calculating Time Differences

```python
from dekad import Dekad

start = Dekad(2024, 1, 1)
end = Dekad(2024, 5, 15)

dekad_start = Dekad.from_date(start)
dekad_end = Dekad.from_date(end)

dekad_diff = dekad_end - dekad_start
print(f"Difference: {dekad_diff} dekads")
```

### Using Dekads in Collections

```python
from dekad import Dekad

# Use in sets
dekad_set = {Dekad(2024, 1), Dekad(2024, 2), Dekad(2024, 1)}
print(len(dekad_set))  # 2 (duplicates removed)

# Use as dictionary keys
data = {
    Dekad(2024, 1): 150.5,
    Dekad(2024, 2): 175.3,
    Dekad(2024, 3): 162.1,
}
```

## Development

### Setting Up Development Environment

This project uses [pixi](https://prefix.dev/docs/pixi/overview) for environment management.

```bash
# Install pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash

# Install dependencies
pixi install

# Activate the development environment
pixi shell -e development
```

### Running Tests

```bash
# Run tests with coverage
pixi run -e test test

# Run in development environment
pixi shell -e development
pytest --cov=src/dekad
```

### Code Quality

```bash
# Check code style and types
pixi run -e development check

# Auto-fix issues
pixi run -e development fix
```

## Requirements

- Python >= 3.9
