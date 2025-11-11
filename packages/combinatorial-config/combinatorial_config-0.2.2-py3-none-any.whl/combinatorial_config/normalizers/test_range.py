"""Tests for range field normalization."""

import pytest
from combinatorial_config.normalizers import Range


class TestRangeToParameters:
    def test_single_value(self):
        assert Range.to_parameters((3,)) == (0, 3, 1)

    def test_two_values(self):
        assert Range.to_parameters((2, 5)) == (2, 5, 1)

    def test_three_values(self):
        assert Range.to_parameters((1, 10, 2)) == (1, 10, 2)

    def test_float_values(self):
        assert Range.to_parameters((0.0, 1.0, 0.1)) == (0.0, 1.0, 0.1)

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            Range.to_parameters(("a",))
        with pytest.raises(ValueError):
            Range.to_parameters((1, "b"))
        with pytest.raises(ValueError):
            Range.to_parameters((1, 2, 3, 4))
        with pytest.raises(ValueError):
            Range.to_parameters([])


class TestRangeToList:
    def test_single_value(self):
        assert Range.to_list((5,)) == [0, 1, 2, 3, 4]

    def test_two_values(self):
        assert Range.to_list((2, 8)) == [2, 3, 4, 5, 6, 7]

    def test_three_values(self):
        assert Range.to_list((1, 10, 2)) == [1, 3, 5, 7, 9]

    def test_float_values(self):
        result = Range.to_list((0.0, 1.0, 0.3))
        assert len(result) == 4
        assert result[0] == 0.0
        assert result[-1] < 1.0

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            Range.to_list(("a",))
