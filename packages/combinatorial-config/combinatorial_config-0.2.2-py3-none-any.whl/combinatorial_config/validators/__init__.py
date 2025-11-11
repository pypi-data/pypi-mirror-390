"""
validators
==========

Validation utilities and type guards for combinatorial configuration schemas.

This subpackage provides functions to check and enforce correctness for fields,
values, sentinel types, and combinatorial objects used throughout the schema
definitions in `combinatorial_config.schemas`.

Functions
---------
is_number_value
    Type guard for numeric values (int | float).
is_primitive_value
    Type guard for primitive values (int | float | str | bool).
is_enumerable_value
    Type guard for enumerable values (primitives | Undefined).
is_range_field
    Type guard for RangeField tuples (start, stop[, step]).
is_enum_field
    Type guard for EnumField tuples of enumerable values.
is_undefined
    Type guard for the Undefined sentinel value.
is_combinatorial_object
    Type guard for CombinatorialObject instances (dict or dataclass with
    all iterable field values).

Submodules
----------
fields
    Validators and type guards for schema field objects (e.g., EnumField, RangeField).
values
    Validators and type guards for scalar or enumerated field values.
escapes
    Validators for special sentinel types such as Undefined.
is_combinatorial_object
    Type guard for validating combinatorial configuration objects.

Notes
-----
All type guard functions follow the TypeGuard pattern, enabling static type
checkers to narrow types when the guard returns True. This provides both
runtime validation and improved static type safety.

Examples
--------
Validating field types:

>>> from combinatorial_config.validators import is_range_field, is_enum_field
>>> is_range_field((0, 10, 2))
True
>>> is_enum_field(("option1", "option2"))
True

Validating values:

>>> from combinatorial_config.validators import is_enumerable_value
>>> is_enumerable_value("foo")
True
>>> is_enumerable_value(42)
True

Validating combinatorial objects:

>>> from combinatorial_config.validators import is_combinatorial_object
>>> config = {
...     "learning_rate": [0.1, 0.01, 0.001],
...     "batch_size": [16, 32, 64]
... }
>>> is_combinatorial_object(config)
True
>>>
>>> invalid_config = {"lr": 0.1, "bs": 32}  # Non-iterable values
>>> is_combinatorial_object(invalid_config)
False
"""

from .is_number_value import is_number_value
from .is_primitive_value import is_primitive_value
from .is_enumerable_value import is_enumerable_value
from .is_range_field import is_range_field
from .is_enum_field import is_enum_field
from .is_undefined import is_undefined
from .is_combinatorial_object import is_combinatorial_object

__all__ = [
    "is_number_value",
    "is_primitive_value",
    "is_enumerable_value",
    "is_range_field",
    "is_enum_field",
    "is_undefined",
    "is_combinatorial_object",
]
