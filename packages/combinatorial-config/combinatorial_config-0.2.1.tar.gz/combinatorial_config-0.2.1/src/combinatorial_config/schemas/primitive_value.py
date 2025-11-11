"""
PrimitiveValue

The union of Python built-in literal types: int, float, str, and bool.

This module defines the PrimitiveValue type alias, representing the union
of Python's built-in literal types. Useful for constraining or validating
the types of settings, options, or combinatorial fields in configuration schemas.

Types
-----
PrimitiveValue : Union[NumberValue, str, bool]
    The union of Python built-in literal types: int, float, str, and bool.

Examples
--------
>>> from combinatorial_config.schemas import PrimitiveValue
>>> value: PrimitiveValue = 1
>>> value: PrimitiveValue = 'foo'
>>> value: PrimitiveValue = True
"""

from typing import Union
from .number_value import NumberValue

PrimitiveValue = Union[NumberValue, str, bool]
"""
The union of Python built-in literal types: int, float, str, and bool.

Notes
-----
Useful for constraining or validating the types of settings, options, or combinatorial fields in configuration schemas.

Examples
--------
>>> value: PrimitiveValue = 1
>>> value: PrimitiveValue = 'foo'
>>> value: PrimitiveValue = True
"""
