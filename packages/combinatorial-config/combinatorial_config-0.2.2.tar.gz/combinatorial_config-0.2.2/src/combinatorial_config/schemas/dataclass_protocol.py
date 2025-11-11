"""
dataclass_protocol
==================

Structural type protocol for dataclass instances.

This module defines a Protocol that captures the structural interface shared by
all dataclass instances, enabling static type checking without requiring explicit
inheritance or runtime registration.

Classes
-------
DataclassProtocol
    Protocol defining the structural interface of dataclass instances.

Notes
-----
The Protocol approach allows for duck-typed checking of dataclass instances
while maintaining compatibility with Python's typing system. Any object that
has the required attributes (`__dataclass_fields__`, `__dataclass_params__`,
`__post_init__`) will be considered compatible with this protocol.

**Important**: This protocol is used only for static type checking (type hints).
For actual runtime validation, use `is_dataclass()` from the `dataclasses` module
instead. The `DataclassProtocol` provides type information to static type checkers,
while `is_dataclass()` performs the actual runtime check to determine if an object
is a dataclass instance.

For example, in `is_combinatorial_object()` validator, `is_dataclass(obj)` is
used for runtime validation, while `DataclassProtocol` is used in type annotations
to indicate that a function accepts dataclass instances.

Examples
--------
>>> from dataclasses import dataclass
>>> from combinatorial_config.schemas import DataclassProtocol
>>>
>>> @dataclass
... class Config:
...     x: int
...     y: str
>>>
>>> def process_dataclass(obj: DataclassProtocol) -> None:
...     # Type checker knows obj has __dataclass_fields__
...     print(obj.__dataclass_fields__.keys())
>>>
>>> config = Config(x=1, y="test")
>>> process_dataclass(config)  # Type checks successfully
"""

from typing import Dict, Any, Optional, Callable, Protocol


class DataclassProtocol(Protocol):
    """
    Structural protocol for dataclass instances.

    This protocol defines the structural interface shared by all Python dataclass
    instances created via the `@dataclass` decorator. It enables type checking
    for dataclass instances without requiring explicit type annotations or
    inheritance relationships.

    Attributes
    ----------
    __dataclass_fields__ : Dict[str, Any]
        Mapping of field names to Field objects containing metadata about each
        field in the dataclass (type, default value, default_factory, etc.).
    __dataclass_params__ : Any
        Parameters used when creating the dataclass (frozen, order, etc.).
        Typically a Params namedtuple from the dataclasses module.
    __post_init__ : Optional[Callable]
        Optional post-initialization hook method that runs after __init__.
        Present if defined in the dataclass, None otherwise.

    Notes
    -----
    This is a Protocol class and should not be instantiated directly. It exists
    purely for static type checking purposes.

    **Runtime Validation**: For actual runtime validation, use `is_dataclass()` from
    the `dataclasses` module instead of this protocol. The `DataclassProtocol` is
    only for type hints and static type checking, while `is_dataclass()` performs
    the actual runtime check.

    The protocol is structural, meaning any object with these three attributes
    will satisfy the type check, even if not explicitly declared as a dataclass.
    However, at runtime, only objects created with the `@dataclass` decorator will
    pass `is_dataclass()` checks.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>> from typing import TYPE_CHECKING
    >>>
    >>> @dataclass
    ... class Point:
    ...     x: float
    ...     y: float
    ...
    ...     def __post_init__(self):
    ...         print(f"Created point at ({self.x}, {self.y})")
    >>>
    >>> def inspect_dataclass(obj: DataclassProtocol) -> list[str]:
    ...     '''Get field names from any dataclass.'''
    ...     return list(obj.__dataclass_fields__.keys())
    >>>
    >>> p = Point(1.0, 2.0)
    >>> inspect_dataclass(p)  # ['x', 'y']
    >>>
    >>> # Access dataclass metadata
    >>> p.__dataclass_fields__['x'].type  # <class 'float'>
    >>> callable(p.__post_init__)  # True
    """

    __dataclass_fields__: Dict[str, Any]
    __dataclass_params__: Any
    __post_init__: Optional[Callable]
