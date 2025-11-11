"""
is_enumerable_value

Type guard for enumerable values (primitives | Undefined).

This module provides a type guard function to validate whether a value is an
EnumerableValue, which is defined as either a PrimitiveValue (int, float, str, bool)
or the Undefined sentinel value.

Functions
---------
is_enumerable_value
    Check if value is a PrimitiveValue or the Undefined sentinel (EnumerableValue).

Examples
--------
>>> from combinatorial_config.validators import is_enumerable_value
>>> from combinatorial_config.schemas import Undefined
>>> is_enumerable_value(Undefined)
True
>>> is_enumerable_value(1)
True
>>> is_enumerable_value("foo")
True
>>> is_enumerable_value([])
False
"""

from typing import Any, TypeGuard
from ..schemas.enumerable_value import EnumerableValue
from ..schemas.undefined import Undefined
from .is_primitive_value import is_primitive_value


def is_enumerable_value(value: Any) -> TypeGuard[EnumerableValue]:
    """
    Check if value is a PrimitiveValue or the Undefined sentinel (EnumerableValue).

    Parameters
    ----------
    value : Any
        Value to check for EnumerableValue type.

    Returns
    -------
    TypeGuard[EnumerableValue]
        True if value is a valid primitive or is Undefined sentinel.

    Examples
    --------
    >>> from combinatorial_config.schemas import Undefined
    >>> is_enumerable_value(Undefined)
    True
    >>> is_enumerable_value(1)
    True
    >>> is_enumerable_value("foo")
    True
    >>> is_enumerable_value([])
    False
    """
    return is_primitive_value(value) or value is Undefined
