"""
EnumerableValue

A value that can be present in enum or literal fields: either a primitive or the Undefined sentinel.

This module defines the EnumerableValue type alias, representing values that
can be enumerated in enum or literal fields. This includes all primitive
values (int, float, str, bool) as well as the Undefined sentinel value.

Types
-----
EnumerableValue : Union[PrimitiveValue, _UndefinedType]
    A value that can be present in enum or literal fields: either a primitive or the Undefined sentinel.

Notes
-----
- Always use `Undefined` from `.undefined` as the runtime value.
- Use `_UndefinedType` only for type annotation.
- This pattern provides the best experience: comparison, assignment, and interface are all always with `Undefined` (the object), while static analysis tools recognize `_UndefinedType`.

Examples
--------
>>> from combinatorial_config.schemas import EnumerableValue, Undefined
>>> v: EnumerableValue = Undefined
>>> v is Undefined
True
>>> v = 3
"""

from typing import Union
from .primitive_value import PrimitiveValue
from ._undefined_type import _UndefinedType

EnumerableValue = Union[PrimitiveValue, _UndefinedType]
"""
A value that can be present in enum or literal fields: either a primitive or the Undefined sentinel.

Notes
-----
- Always use `Undefined` from `.undefined` as the runtime value.
- Use `_UndefinedType` only for type annotation.
- This pattern provides the best experience: comparison, assignment, and interface are all always with `Undefined` (the object), while static analysis tools recognize `_UndefinedType`.

Examples
--------
>>> from combinatorial_config.schemas import Undefined
>>> v: EnumerableValue = Undefined
>>> v is Undefined
True
>>> v = 3
"""
