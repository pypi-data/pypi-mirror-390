"""A set of common utilities for MessagePack handling."""

from typing import Protocol


class EnumWithBounds(Protocol):
    """Protocol for enums with low and high bounds."""

    low: int
    high: int


def in_range(n: int, enum: EnumWithBounds) -> bool:
    """Check if n is within the bounds of the given enum.

    Args:
        n: The value to check.
        enum: An enum with 'low' and 'high' attributes.

    Returns:
        bool: True if n is within the bounds, False otherwise.
    """
    return enum.low <= n <= enum.high
