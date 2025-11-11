"""
is_number_value

Type guard for numeric values (int | float).

This module provides a type guard function to validate whether a value is a
NumberValue, which is defined as either an int or float.

Functions
---------
is_number_value
    Check if value is an int or float (NumberValue).

Examples
--------
>>> from combinatorial_config.validators import is_number_value
>>> is_number_value(1)
True
>>> is_number_value(1.234)
True
>>> is_number_value("1")
False
"""

from typing import Any, TypeGuard
from ..schemas.number_value import NumberValue


def is_number_value(value: Any) -> TypeGuard[NumberValue]:
    """
    Check if value is an int or float (NumberValue).

    Parameters
    ----------
    value : Any
        Value to check for NumberValue type.

    Returns
    -------
    TypeGuard[NumberValue]
        True if value is int or float, False otherwise.

    Examples
    --------
    >>> is_number_value(1)
    True
    >>> is_number_value(1.234)
    True
    >>> is_number_value("1")
    False
    """
    return isinstance(value, (int, float))
