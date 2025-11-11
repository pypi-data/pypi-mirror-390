"""Utility functions for working with Dekad objects."""

from collections.abc import Iterator

from dekad.dekad import Dekad


def dekad_range(start: Dekad, end: Dekad, step: int = 1) -> Iterator[Dekad]:
    """Generate a range of Dekad objects.

    Similar to Python's built-in range() function, but for Dekad objects.
    The range is inclusive of start but exclusive of end.

    Args:
        start: The starting Dekad (inclusive).
        end: The ending Dekad (exclusive).
        step: The step size in dekads (default 1). Can be negative.

    Yields:
        Dekad objects in the specified range.

    Raises:
        ValueError: If step is 0 or if the range would be infinite.

    Examples:
        >>> from dekad import Dekad, dekad_range
        >>> list(dekad_range(Dekad(2024, 1), Dekad(2024, 4)))
        [Dekad(2024, 1), Dekad(2024, 2), Dekad(2024, 3)]
        >>> list(dekad_range(Dekad(2024, 5), Dekad(2024, 2), -1))
        [Dekad(2024, 5), Dekad(2024, 4), Dekad(2024, 3)]

    """
    if step == 0:
        msg = 'Step cannot be zero'
        raise ValueError(msg)

    if step > 0 and start >= end:
        return
    if step < 0 and start <= end:
        return

    current = start
    if step > 0:
        while current < end:
            yield current
            current = current + step
    else:
        while current > end:
            yield current
            current = current + step
