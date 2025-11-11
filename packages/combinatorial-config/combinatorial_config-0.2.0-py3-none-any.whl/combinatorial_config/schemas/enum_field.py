"""
EnumField

A tuple of values to be enumerated, each can be a primitive type or the Undefined sentinel value.

This module defines the EnumField type alias, representing tuples of enumerable
values that can be used to specify admissible field options in combinatorial
configurations.

Types
-----
EnumField : Tuple[EnumerableValue, ...]
    A tuple of values to be enumerated, each can be a primitive type or the Undefined sentinel value.

Examples
--------
>>> from combinatorial_config.schemas import EnumField, Undefined
>>> colors: EnumField = ("red", "green", "blue")
>>> extended: EnumField = ("yes", "no", Undefined)
"""

from typing import Tuple
from .enumerable_value import EnumerableValue

EnumField = Tuple[EnumerableValue, ...]
"""
A tuple of values to be enumerated, each can be a primitive type or the Undefined sentinel value.

Examples
--------
>>> from combinatorial_config.schemas import Undefined
>>> colors: EnumField = ("red", "green", "blue")
>>> extended: EnumField = ("yes", "no", Undefined)
"""
