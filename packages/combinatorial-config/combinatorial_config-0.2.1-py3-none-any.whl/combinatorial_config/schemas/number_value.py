"""
NumberValue

Type alias for integers or floating-point values.

This module defines the NumberValue type alias, representing numeric values
that can be either integers or floating-point numbers. Used widely for
numerical parameters—both continuous and discrete—such as values in ranges,
configuration, and computation.

Types
-----
NumberValue : Union[int, float]
    Type alias for integers or floating-point values.

Examples
--------
>>> from combinatorial_config.schemas import NumberValue
>>> a: NumberValue = 3
>>> b: NumberValue = 3.14
"""

from typing import Union

NumberValue = Union[int, float]
"""
A type alias for integers or floating-point values.

Notes
-----
Used widely for numerical parameters—both continuous and discrete—such as values in ranges, configuration, and computation.

Examples
--------
>>> a: NumberValue = 3
>>> b: NumberValue = 3.14
"""
