"""
is_primitive_value

Type guard for primitive values (int | float | str | bool).

This module provides a type guard function to validate whether a value is a
PrimitiveValue, which is defined as one of the Python built-in literal types:
int, float, str, or bool.

Functions
---------
is_primitive_value
    Check if value is int, float, str, or bool (PrimitiveValue).

Examples
--------
>>> from combinatorial_config.validators import is_primitive_value
>>> is_primitive_value(0)
True
>>> is_primitive_value("foo")
True
>>> is_primitive_value(False)
True
>>> is_primitive_value([1, 2])
False
"""

from typing import Any, TypeGuard
from ..schemas.primitive_value import PrimitiveValue


def is_primitive_value(value: Any) -> TypeGuard[PrimitiveValue]:
    """
    Check if value is int, float, str, or bool (PrimitiveValue).

    Parameters
    ----------
    value : Any
        Value to check for PrimitiveValue type.

    Returns
    -------
    TypeGuard[PrimitiveValue]
        True if value is int, float, str, or bool; otherwise False.

    Examples
    --------
    >>> is_primitive_value(0)
    True
    >>> is_primitive_value("foo")
    True
    >>> is_primitive_value(False)
    True
    >>> is_primitive_value([1, 2])
    False
    """
    return isinstance(value, (int, float, str, bool))
