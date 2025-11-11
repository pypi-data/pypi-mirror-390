"""
is_enum_field

Type guard for EnumField tuples of enumerable values.

This module provides a type guard function to validate whether a value conforms
to the EnumField specification, which is a tuple of one or more enumerable
values (primitives or Undefined sentinel).

Functions
---------
is_enum_field
    Check if a value is a tuple with one or more enum-allowed elements
    (primitive or Undefined sentinel).

Notes
-----
EnumField is defined as a tuple of EnumerableValue (PrimitiveValue | Undefined)
elements. This validator ensures the value matches this specification.

Examples
--------
>>> from combinatorial_config.validators import is_enum_field
>>> from combinatorial_config.schemas import Undefined
>>> is_enum_field(("on", "off"))
True
>>> is_enum_field(("yes", Undefined))
True
>>> is_enum_field((1, 2, None))
False
>>> is_enum_field((True,))
True
>>> is_enum_field([])
False
"""

from typing import Any, TypeGuard
from ..schemas.enum_field import EnumField


def is_enum_field(value: Any) -> TypeGuard[EnumField]:
    """
    Check if value is a tuple with one or more enum-allowed elements (primitive or Undefined sentinel).

    Parameters
    ----------
    value : Any
        Value to check for EnumField type.

    Returns
    -------
    TypeGuard[EnumField]
        True if value is a tuple, length >= 1, all entries are primitive or Undefined sentinel.

    Examples
    --------
    >>> from combinatorial_config.schemas import Undefined
    >>> is_enum_field(("on", "off"))
    True
    >>> is_enum_field(("yes", Undefined))
    True
    >>> is_enum_field((1, 2, None))
    False
    >>> is_enum_field((True,))
    True
    >>> is_enum_field([])
    False
    """
    if not isinstance(value, tuple):
        return False
    if len(value) == 0:
        return False
    return all(
        isinstance(v, (int, float, str, bool)) or type(v).__name__ == "_UndefinedType"
        for v in value
    )
