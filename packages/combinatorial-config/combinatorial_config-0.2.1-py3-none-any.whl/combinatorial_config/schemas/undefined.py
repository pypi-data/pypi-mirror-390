"""
undefined

A sentinel value representing an undefined or unspecified field.

This module defines the Undefined singleton instance, which represents
undefined or unspecified values in schemas, enums, or optional fields.

Values
------
Undefined : _UndefinedType
    A singleton sentinel object representing 'undefined' or unspecified values
    in schemas, enums, or optional fields.

Notes
-----
- Use `Undefined` for fields where `None` may be a valid value, but you still
  need to distinguish "not specified at all".
- Use identity comparison (`is Undefined`) to check for this sentinel.
- Never use `_UndefinedType` as a value; always use `Undefined` (the instance).
- Inspired by sentinel design in numpy, typing, and enum patterns in Python libraries.

Examples
--------
>>> from combinatorial_config.schemas import Undefined
>>> field = Undefined
>>> field is Undefined
True
>>> bool(field)
False
>>> # Use in optional fields
>>> from combinatorial_config.schemas import EnumField
>>> options: EnumField = ("yes", "no", Undefined)
"""

from ._undefined_type import _UndefinedType

Undefined = _UndefinedType()
"""
A sentinel value representing an undefined or unspecified field.

Notes
-----
Used in enums or optional fields to distinguish between "not provided" and None.
Useful when None is a valid value but you need to represent "no value specified".

Examples
--------
>>> field = Undefined
>>> field is Undefined
True
>>> bool(field)
False
"""
