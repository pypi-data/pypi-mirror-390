"""
combinatorial_object
====================

Type alias for objects that can be used as combinatorial configurations.

This module defines the CombinatorialObject type, representing configuration
objects where all field values are intended to be iterable collections. The
type is defined broadly at the static type level but is enforced strictly
at runtime via type guard functions.

Types
-----
CombinatorialObject : Union[Dict, DataclassProtocol]
    Type alias for objects that can represent combinatorial configurations.
    Valid objects are either dictionaries or dataclass instances where all
    field values must be iterable (excluding strings).

Notes
-----
The CombinatorialObject type provides a flexible static type definition while
relying on runtime validation (via `is_combinatorial_object` type guard) to
enforce the stricter constraint that all field values must be iterable.

This design choice enables:
- Flexible static typing that works with standard dicts and dataclasses
- Strict runtime validation ensuring all values are iterable
- Type narrowing via TypeGuard for improved type safety

String values are explicitly excluded from valid field values despite being
technically iterable, as they represent atomic scalar values in the context
of combinatorial configurations rather than collections to iterate over.

The typical workflow is:
1. Define a dict or dataclass with collection-typed fields
2. Validate it at runtime using `is_combinatorial_object()`
3. Generate combinations by iterating over all field values

Examples
--------
Valid combinatorial objects (dict-based):

>>> from typing import Dict
>>> config: Dict = {
...     "learning_rate": [0.1, 0.01, 0.001],
...     "batch_size": [16, 32, 64],
...     "dropout": [0.1, 0.2, 0.3]
... }
>>> # Each field value is a list of options to explore

Valid combinatorial objects (dataclass-based):

>>> from dataclasses import dataclass
>>>
>>> @dataclass
... class HyperParams:
...     learning_rates: list[float]
...     batch_sizes: tuple[int, ...]
...     epochs: list[int]
>>>
>>> params = HyperParams(
...     learning_rates=[0.1, 0.01],
...     batch_sizes=(16, 32, 64),
...     epochs=[10, 20, 30]
... )
>>> # All fields contain collections of parameter values

Runtime validation:

>>> from combinatorial_config.validators import is_combinatorial_object
>>>
>>> valid_cfg = {"lr": [0.1, 0.01], "bs": [16, 32]}
>>> if is_combinatorial_object(valid_cfg):
...     # Type is narrowed to CombinatorialObject here
...     print("Valid configuration")
>>>
>>> invalid_cfg = {"lr": 0.1, "bs": 32}  # Scalar values
>>> is_combinatorial_object(invalid_cfg)  # False

See Also
--------
is_combinatorial_object : Type guard function for runtime validation
DataclassProtocol : Structural protocol for dataclass instances
"""

from typing import Union, Dict
from .dataclass_protocol import DataclassProtocol


CombinatorialObject = Union[Dict, DataclassProtocol]
"""
Type alias for combinatorial configuration objects.

A CombinatorialObject can be either:
- A dict where all values are iterable (excluding strings)
- A dataclass instance where all field values are iterable (excluding strings)

The static type is broad (Dict | DataclassProtocol) but runtime validation
via `is_combinatorial_object()` enforces that all field values must be
iterable collections.

Type
----
Union[Dict, DataclassProtocol]

Notes
-----
Use `is_combinatorial_object()` to validate objects at runtime before using
them for combinatorial operations. The TypeGuard will narrow the type for
improved type safety in subsequent code.

Examples
--------
>>> from typing import Dict
>>> cfg: Dict = {"lr": [0.1, 0.01], "bs": [16, 32]}
>>> # cfg is a valid CombinatorialObject candidate
>>>
>>> from dataclasses import dataclass
>>> @dataclass
... class Config:
...     lrs: list[float]
...     bss: list[int]
>>>
>>> obj = Config([0.1, 0.01], [16, 32])
>>> # obj is a valid CombinatorialObject candidate
"""
