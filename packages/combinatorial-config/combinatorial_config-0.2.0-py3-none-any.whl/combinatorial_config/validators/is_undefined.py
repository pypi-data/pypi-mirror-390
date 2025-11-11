"""
is_undefined

Type guard and identity check for the Undefined sentinel value.

This module provides a type guard function to validate whether a value is the
Undefined sentinel object used in schemas for representing undefined or
unspecified field values.

Functions
---------
is_undefined
    Check if value is the Undefined sentinel object.

Notes
-----
- `_UndefinedType` is the type (class) of the sentinel; use this only for type annotations or TypeGuard.
- `Undefined` is the unique singleton value used at runtime; always use and compare this value (e.g. `is Undefined`) in your code and logic.
- Never assign, use, or compare `_UndefinedType` as a value; it is not the sentinel instance.
- When type-hinting, use `_UndefinedType` in unions, but at runtime, assign and check only `Undefined`.
- This separation is necessary for compatibility with Python's typing/type-checker system, which doesn't allow using runtime values (like `Undefined`) as true types.

Examples
--------
>>> from combinatorial_config.schemas import Undefined
>>> from combinatorial_config.validators import is_undefined
>>> is_undefined(Undefined)
True
>>> is_undefined(None)
False
"""

from ..schemas.undefined import Undefined
from ..schemas._undefined_type import _UndefinedType
from typing import Any, TypeGuard


def is_undefined(value: Any) -> TypeGuard[_UndefinedType]:
    """
    Check if value is the Undefined sentinel object.

    Parameters
    ----------
    value : Any
        The value to test.

    Returns
    -------
    TypeGuard[_UndefinedType]
        True if and only if value is the Undefined sentinel instance.
    """
    return value is Undefined
