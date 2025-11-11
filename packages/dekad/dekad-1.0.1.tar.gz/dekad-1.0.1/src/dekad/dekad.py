"""Dekad class for handling 10-day periods."""

import calendar
import datetime
from typing import Union


class Dekad:
    """Represents a dekad (10-day period) in the calendar system.

    Each month is divided into 3 dekads:
    - Dekad 1: days 1-10
    - Dekad 2: days 11-20
    - Dekad 3: days 21 to end of month

    Each year has 36 dekads (12 months x 3 dekads).

    Attributes:
        year: The year of the dekad.
        dekad_of_year: The dekad number within the year (1-36).

    """

    def __init__(self, year: int, dekad_of_year: int) -> None:
        """Initialize a Dekad object.

        Args:
            year: The year (must be positive).
            dekad_of_year: The dekad number within the year (1-36).

        Raises:
            ValueError: If year is not positive or dekad_of_year is not in
                range 1-36.

        """
        if year <= 0:
            msg = f'Year must be positive, got {year}'
            raise ValueError(msg)
        if not 1 <= dekad_of_year <= 36:
            msg = (
                f'Dekad of year must be between 1 and 36, got {dekad_of_year}'
            )
            raise ValueError(msg)

        self._year = year
        self._dekad_of_year = dekad_of_year

    @classmethod
    def from_date(cls, date: datetime.date) -> 'Dekad':
        """Create a Dekad from a date.

        Args:
            date: The date to convert.

        Returns:
            A Dekad object corresponding to the date.

        """
        month = date.month
        day = date.day

        # Determine which dekad of the month (1, 2, or 3)
        if day <= 10:
            dekad_of_month = 1
        elif day <= 20:
            dekad_of_month = 2
        else:
            dekad_of_month = 3

        dekad_of_year = (month - 1) * 3 + dekad_of_month
        return cls(date.year, dekad_of_year)

    @classmethod
    def from_ymd(cls, year: int, month: int, dekad_of_month: int) -> 'Dekad':
        """Create a Dekad from year, month, and dekad of month.

        Args:
            year: The year.
            month: The month (1-12).
            dekad_of_month: The dekad number within the month (1-3).

        Returns:
            A Dekad object.

        Raises:
            ValueError: If month is not in range 1-12 or dekad_of_month is
                not in range 1-3.

        """
        if not 1 <= month <= 12:
            msg = f'Month must be between 1 and 12, got {month}'
            raise ValueError(msg)
        if not 1 <= dekad_of_month <= 3:
            msg = (
                f'Dekad of month must be between 1 and 3, got {dekad_of_month}'
            )
            raise ValueError(msg)

        dekad_of_year = (month - 1) * 3 + dekad_of_month
        return cls(year, dekad_of_year)

    @property
    def year(self) -> int:
        """Return the year of the dekad."""
        return self._year

    @property
    def dekad_of_year(self) -> int:
        """Return the dekad number within the year (1-36)."""
        return self._dekad_of_year

    @property
    def month(self) -> int:
        """Return the month (1-12) derived from dekad_of_year."""
        return (self._dekad_of_year - 1) // 3 + 1

    @property
    def dekad_of_month(self) -> int:
        """Return the dekad number within the month (1-3)."""
        return (self._dekad_of_year - 1) % 3 + 1

    def first_date(self) -> datetime.date:
        """Return the first date of the dekad.

        Returns:
            The first date of the dekad.

        """
        month = self.month
        dekad_of_month = self.dekad_of_month

        if dekad_of_month == 1:
            day = 1
        elif dekad_of_month == 2:
            day = 11
        else:  # dekad_of_month == 3
            day = 21

        return datetime.date(self._year, month, day)

    def last_date(self) -> datetime.date:
        """Return the last date of the dekad.

        Returns:
            The last date of the dekad.

        """
        month = self.month
        dekad_of_month = self.dekad_of_month

        if dekad_of_month == 1:
            day = 10
        elif dekad_of_month == 2:
            day = 20
        else:  # dekad_of_month == 3
            # Get the last day of the month
            _, last_day = calendar.monthrange(self._year, month)
            day = last_day

        return datetime.date(self._year, month, day)

    def __add__(self, other: int) -> 'Dekad':
        """Add dekads.

        Args:
            other: Number of dekads to add.

        Returns:
            A new Dekad object.

        Raises:
            TypeError: If other is not an integer.

        """
        if not isinstance(other, int):
            msg = f'Can only add integers to Dekad, got {type(other)}'
            raise TypeError(msg)

        # Calculate total dekads from year 1
        total_dekads = (self._year - 1) * 36 + self._dekad_of_year + other

        if total_dekads <= 0:
            msg = f'Resulting dekad would be non-positive: {total_dekads}'
            raise ValueError(msg)

        # Convert back to year and dekad_of_year
        new_year = (total_dekads - 1) // 36 + 1
        new_dekad_of_year = (total_dekads - 1) % 36 + 1

        return Dekad(new_year, new_dekad_of_year)

    def __radd__(self, other: int) -> 'Dekad':
        """Support int + Dekad.

        Args:
            other: Number of dekads to add.

        Returns:
            A new Dekad object.

        """
        return self.__add__(other)

    def __sub__(self, other: Union[int, 'Dekad']) -> Union['Dekad', int]:
        """Subtract dekads or calculate difference.

        Args:
            other: Either an integer (number of dekads to subtract) or
                another Dekad (to calculate difference).

        Returns:
            If other is an integer, returns a new Dekad.
            If other is a Dekad, returns the difference in dekads (int).

        Raises:
            TypeError: If other is neither an integer nor a Dekad.

        """
        if isinstance(other, int):
            return self.__add__(-other)
        if isinstance(other, Dekad):
            # Calculate difference in dekads
            total_self = (self._year - 1) * 36 + self._dekad_of_year
            total_other = (other._year - 1) * 36 + other._dekad_of_year
            return total_self - total_other

        msg = (
            f'Can only subtract integers or Dekad from Dekad, '
            f'got {type(other)}'
        )
        raise TypeError(msg)

    def __rsub__(self, other: int) -> 'Dekad':
        """Raise error for int - Dekad.

        Args:
            other: An integer.

        Raises:
            TypeError: Always, as this operation is not supported.

        """
        msg = 'Cannot subtract Dekad from integer'
        raise TypeError(msg)

    def __eq__(self, other: object) -> bool:
        """Check equality with another Dekad.

        Args:
            other: Object to compare with.

        Returns:
            True if equal, False otherwise.

        """
        if not isinstance(other, Dekad):
            return NotImplemented
        return (
            self._year == other._year
            and self._dekad_of_year == other._dekad_of_year
        )

    def __lt__(self, other: 'Dekad') -> bool:
        """Check if this dekad is less than another.

        Args:
            other: Dekad to compare with.

        Returns:
            True if this dekad is earlier, False otherwise.

        """
        if not isinstance(other, Dekad):
            return NotImplemented
        if self._year != other._year:
            return self._year < other._year
        return self._dekad_of_year < other._dekad_of_year

    def __le__(self, other: 'Dekad') -> bool:
        """Check if this dekad is less than or equal to another.

        Args:
            other: Dekad to compare with.

        Returns:
            True if this dekad is earlier or equal, False otherwise.

        """
        if not isinstance(other, Dekad):
            return NotImplemented
        return self == other or self < other

    def __gt__(self, other: 'Dekad') -> bool:
        """Check if this dekad is greater than another.

        Args:
            other: Dekad to compare with.

        Returns:
            True if this dekad is later, False otherwise.

        """
        if not isinstance(other, Dekad):
            return NotImplemented
        return not self <= other

    def __ge__(self, other: 'Dekad') -> bool:
        """Check if this dekad is greater than or equal to another.

        Args:
            other: Dekad to compare with.

        Returns:
            True if this dekad is later or equal, False otherwise.

        """
        if not isinstance(other, Dekad):
            return NotImplemented
        return not self < other

    def __ne__(self, other: object) -> bool:
        """Check inequality with another Dekad.

        Args:
            other: Object to compare with.

        Returns:
            True if not equal, False otherwise.

        """
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        """Return hash of the dekad.

        Returns:
            Hash value for use in sets and as dictionary keys.

        """
        return hash((self._year, self._dekad_of_year))

    def __str__(self) -> str:
        """Return user-friendly string representation.

        Returns:
            String in format "2024-D15".

        """
        return f'{self._year}-D{self._dekad_of_year:02d}'

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            String in format "Dekad(2024, 15)".

        """
        return f'Dekad({self._year}, {self._dekad_of_year})'
