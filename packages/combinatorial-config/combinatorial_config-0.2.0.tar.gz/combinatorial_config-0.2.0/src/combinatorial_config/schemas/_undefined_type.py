"""
_undefined_type

Sentinel type representing an undefined or unspecified value.

This module defines the _UndefinedType class, which is a singleton pattern
implementation for representing undefined or unspecified values in schemas,
enums, or optional fields.

Classes
-------
_UndefinedType
    Sentinel type representing an undefined or unspecified value.

Notes
-----
- This is a singleton class - only one instance should exist.
- Use `Undefined` (the instance) for runtime values.
- Use `_UndefinedType` only for type annotations.
- Never instantiate this class directly; use the `Undefined` instance instead.

Examples
--------
>>> from combinatorial_config.schemas import Undefined, _UndefinedType
>>> field: _UndefinedType = Undefined
>>> field is Undefined
True
>>> bool(field)
False
"""

from typing import Union


class _UndefinedType:
    """Sentinel type representing an undefined or unspecified value."""

    _instance: Union["_UndefinedType", None] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "Undefined"

    def __bool__(self) -> bool:
        return False
