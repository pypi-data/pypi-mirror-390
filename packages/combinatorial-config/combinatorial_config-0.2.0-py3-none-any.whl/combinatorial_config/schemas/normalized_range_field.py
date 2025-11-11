"""
NormalizedRangeField

A tuple of exactly three NumberValue values representing a normalized range: (start, stop, step).

This module defines the NormalizedRangeField type alias, representing the
canonical/normalized representation of ranges in processing or computation.
This structure enables uniform handling of all ranges.

Types
-----
NormalizedRangeField : Tuple[NumberValue, NumberValue, NumberValue]
    A tuple of exactly three NumberValue values representing a normalized range: (start, stop, step).

Notes
-----
Used for canonical/normalized representation of ranges in processing or computation. This structure enables uniform handling of all ranges.

Examples
--------
>>> from combinatorial_config.schemas import NormalizedRangeField
>>> nrf: NormalizedRangeField = (0, 10, 1)
>>> nrf2: NormalizedRangeField = (1.0, 10.0, 0.5)
"""

from typing import Tuple
from .number_value import NumberValue

NormalizedRangeField = Tuple[NumberValue, NumberValue, NumberValue]
"""
A tuple of exactly three NumberValue values representing a normalized range: (start, stop, step).

Notes
-----
Used for canonical/normalized representation of ranges in processing or computation. This structure enables uniform handling of all ranges.

Examples
--------
>>> nrf: NormalizedRangeField = (0, 10, 1)
>>> nrf2: NormalizedRangeField = (1.0, 10.0, 0.5)
"""
