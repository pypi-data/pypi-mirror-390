"""
schemas
=======

Canonical type building blocks, field representations, and explicit sentinels
for combinatorial configuration schemas.

This package unifies all types, value unions, range and enum field specs, sentinel
values, structural protocols, and combinatorial object types for strict schema
construction, validation, and runtime editing of configuration domains.

Exports
-------
NumberValue : int | float
    Numeric types for scalar/range fields (e.g. parameter bounds, step sizes).
PrimitiveValue : int | float | str | bool
    Literal types allowed for direct user input or as enum/literal values.
EnumerableValue : PrimitiveValue | _UndefinedType
    Union for values that enumerate primitives and the explicit "Undefined" sentinel
    for optional/unspecified states. Used for enums, option sets, etc.
RangeField : tuple
    Tuple of 1-3 int/float (start, stop[, step]), with normalization utilities available.
NormalizedRangeField : tuple
    Strict 3-tuple (start, stop, step) normalizing all RangeField forms.
EnumField : tuple
    One or more EnumerableValue instances specifying admissible field options.
Undefined : _UndefinedType instance
    Singleton sentinel for fields explicitly 'not set' or 'unspecified'. Use for
    runtime logic and assignments, and compare with `is` (identity check only).
_UndefinedType : type
    Sentinel class (never instantiate yourself). For use only in type annotations.
DataclassProtocol : Protocol
    Structural protocol defining the interface of dataclass instances. Enables
    static type checking for dataclass objects without explicit inheritance.
CombinatorialObject : Union[Dict, DataclassProtocol]
    Type alias for configuration objects where all field values are iterable.
    Represents either a dict or dataclass instance suitable for generating
    combinatorial configurations. Use with `is_combinatorial_object()` for
    runtime validation.

Design
------
- Types and sentinels are organized in submodules (values, fields, escapes,
  dataclass_protocol, combinatorial_object) for clarity and strict import hygiene.
- Use Undefined for value assignment/check; use _UndefinedType in `Union` or
  function signatures for static type checking only.
- Explicit separation of runtime value and type avoids silent None-misuse and
  increases type safety for users and library code.
- RangeField/EnumField specs are always tuples. Accepts both ints and floats,
  and is validated/normalized before use in algorithms.
- DataclassProtocol provides structural typing for dataclass instances, enabling
  generic functions that operate on any dataclass without explicit type parameters.
- CombinatorialObject provides a type alias for configuration objects with iterable
  field values. The type is broad at the static level but enforced strictly at
  runtime via type guards.

Submodules
----------
values
    Fundamental and derived value types; unions for primitive/configured values.
fields
    Field representations and constraints for ranges, enums, and normalized forms.
escapes
    Sentinel type and singleton value for undefined/unspecified field values.
dataclass_protocol
    Structural protocol for typing dataclass instances.
combinatorial_object
    Type alias for combinatorial configuration objects.

Examples
--------
Basic field types and sentinels:

>>> from combinatorial_config.schemas import EnumField, Undefined, RangeField
>>> bar: EnumField = ("on", "off", Undefined)
>>> assert bar[2] is Undefined
>>> rf: RangeField = (9, 10)
>>> # All types strictly typed, normalized and validated for downstream logic

Using DataclassProtocol for generic dataclass functions:

>>> from combinatorial_config.schemas import DataclassProtocol
>>> from dataclasses import dataclass
>>>
>>> @dataclass
... class Config:
...     learning_rate: float
...     batch_size: int
>>>
>>> def get_fields(obj: DataclassProtocol) -> list[str]:
...     '''Extract field names from any dataclass.'''
...     return list(obj.__dataclass_fields__.keys())
>>>
>>> cfg = Config(0.001, 32)
>>> get_fields(cfg)  # ['learning_rate', 'batch_size']

Using CombinatorialObject for combinatorial configurations:

>>> from combinatorial_config.schemas import CombinatorialObject
>>> from combinatorial_config.validators import is_combinatorial_object
>>>
>>> config = {
...     "learning_rate": [0.1, 0.01, 0.001],
...     "batch_size": [16, 32, 64]
... }
>>>
>>> if is_combinatorial_object(config):
...     # Type is narrowed to CombinatorialObject
...     # Now safe to generate combinations
...     print("Valid combinatorial config")
"""

from .number_value import NumberValue
from .primitive_value import PrimitiveValue
from .enumerable_value import EnumerableValue
from .range_field import RangeField
from .normalized_range_field import NormalizedRangeField
from .enum_field import EnumField
from .undefined import Undefined
from ._undefined_type import _UndefinedType
from .dataclass_protocol import DataclassProtocol
from .combinatorial_object import CombinatorialObject

__all__ = [
    "NumberValue",
    "PrimitiveValue",
    "EnumerableValue",
    "RangeField",
    "NormalizedRangeField",
    "EnumField",
    "Undefined",
    "_UndefinedType",
    "DataclassProtocol",
    "CombinatorialObject",
]
