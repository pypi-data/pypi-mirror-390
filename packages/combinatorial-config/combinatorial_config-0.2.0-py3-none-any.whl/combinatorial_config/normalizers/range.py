"""Range field normalization utilities."""

import numpy as np
from ..schemas import NumberValue, RangeField, NormalizedRangeField
from ..validators import is_range_field


class Range:
    """Normalization utilities for RangeField."""

    @staticmethod
    def to_parameters(value: RangeField) -> NormalizedRangeField:
        """
        Normalize RangeField to a standard 3-tuple (start, stop, step).

        Converts various RangeField formats to a normalized representation:
        - (stop,) -> (0, stop, 1)
        - (start, stop) -> (start, stop, 1)
        - (start, stop, step) -> (start, stop, step)

        Parameters
        ----------
        value : RangeField
            A tuple of 1-3 numeric values representing a range.

        Returns
        -------
        NormalizedRangeField
            A 3-tuple (start, stop, step) with all values normalized.

        Raises
        ------
        ValueError
            If value is not a valid RangeField.

        Examples
        --------
        >>> Range.to_parameters((5,))
        (0, 5, 1)
        >>> Range.to_parameters((2, 8))
        (2, 8, 1)
        >>> Range.to_parameters((1, 10, 2))
        (1, 10, 2)
        >>> Range.to_parameters((0.0, 1.0, 0.1))
        (0.0, 1.0, 0.1)
        """
        if not is_range_field(value):
            raise ValueError(f"Invalid range field: {value}")

        if len(value) == 1:
            return (0, value[0], 1)
        elif len(value) == 2:
            return (value[0], value[1], 1)
        elif len(value) == 3:
            return (value[0], value[1], value[2])
        else:
            raise ValueError(f"Invalid range field: {value}")

    @staticmethod
    def to_list(value: RangeField) -> list[NumberValue]:
        """
        Convert RangeField to a list of numeric values using numpy.arange.

        Parameters
        ----------
        value : RangeField
            A tuple of 1-3 numeric values representing a range.

        Returns
        -------
        list[NumberValue]
            A list of numeric values generated from the range.

        Raises
        ------
        ValueError
            If value is not a valid RangeField.

        Examples
        --------
        >>> Range.to_list((5,))
        [0, 1, 2, 3, 4]
        >>> Range.to_list((2, 8))
        [2, 3, 4, 5, 6, 7]
        >>> Range.to_list((1, 10, 2))
        [1, 3, 5, 7, 9]
        """
        start, stop, step = Range.to_parameters(value)
        return np.arange(start, stop, step).tolist()
