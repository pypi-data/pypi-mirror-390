"""
is_range_field

Type guard for RangeField tuples (start, stop[, step]).

This module provides a type guard function to validate whether a value conforms
to the RangeField specification, which is a tuple of 1, 2, or 3 numeric values
representing a numeric range.

Functions
---------
is_range_field
    Check if a value is a tuple with 1, 2, or 3 numeric (int or float) elements,
    suitable for RangeField.

Notes
-----
RangeField is defined as a tuple of 1-3 NumberValue (int | float) elements,
representing (start, [stop], [step]). This validator ensures the value matches
this specification.

Examples
--------
>>> from combinatorial_config.validators import is_range_field
>>> is_range_field((5,))
True
>>> is_range_field((1, 10, 2))
True
>>> is_range_field((1, 2, 3, 4))
False
>>> is_range_field([1, 2])
False
"""

from typing import Any, TypeGuard
from ..schemas.range_field import RangeField


def is_range_field(value: Any) -> TypeGuard[RangeField]:
    """
    Check if value is a tuple with 1, 2, or 3 numeric (int or float) elements, suitable for RangeField.

    Parameters
    ----------
    value : Any
        Value to check for RangeField type.

    Returns
    -------
    TypeGuard[RangeField]
        True if value is a tuple with 1-3 int or float entries, False otherwise.

    Examples
    --------
    >>> is_range_field((5,))
    True
    >>> is_range_field((1, 10, 2))
    True
    >>> is_range_field((1, 2, 3, 4))
    False
    >>> is_range_field([1, 2])
    False
    """
    if not isinstance(value, tuple):
        return False
    if len(value) not in {1, 2, 3}:
        return False
    return all(isinstance(v, (int, float)) for v in value)
