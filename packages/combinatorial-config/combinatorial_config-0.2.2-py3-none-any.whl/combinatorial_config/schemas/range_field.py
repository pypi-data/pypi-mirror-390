"""
RangeField

A tuple of 1, 2, or 3 NumberValue values representing a numeric range: (start, [stop], [step]).

This module defines the RangeField type alias, representing tuples that specify
numeric ranges suitable for use with constructs like Python's range or numpy.linspace.

Types
-----
RangeField : Union[Tuple[NumberValue], Tuple[NumberValue, NumberValue], Tuple[NumberValue, NumberValue, NumberValue]]
    A tuple of 1, 2, or 3 NumberValue values representing a numeric range: (start, [stop], [step]).

Notes
-----
Suitable for use with constructs like Python's range or numpy.linspace. If only 1 or 2 elements are provided, defaults are assumed for omitted values (e.g., start=0, step=1).

Examples
--------
>>> from combinatorial_config.schemas import RangeField
>>> rf1: RangeField = (10,)       # Only stop; treated as (0, 10, 1)
>>> rf2: RangeField = (2, 8)      # start, stop; treated as (2, 8, 1)
>>> rf3: RangeField = (1, 10, 2)  # start, stop, step
"""

from typing import Union, Tuple
from .number_value import NumberValue

RangeField = Union[
    Tuple[NumberValue],
    Tuple[NumberValue, NumberValue],
    Tuple[NumberValue, NumberValue, NumberValue],
]
"""
A tuple of 1, 2, or 3 NumberValue values representing a numeric range: (start, [stop], [step]).

Notes
-----
Suitable for use with constructs like Python's range or numpy.linspace. If only 1 or 2 elements are provided, defaults are assumed for omitted values (e.g., start=0, step=1).

Examples
--------
>>> rf1: RangeField = (10,)       # Only stop; treated as (0, 10, 1)
>>> rf2: RangeField = (2, 8)      # start, stop; treated as (2, 8, 1)
>>> rf3: RangeField = (1, 10, 2)  # start, stop, step
"""
