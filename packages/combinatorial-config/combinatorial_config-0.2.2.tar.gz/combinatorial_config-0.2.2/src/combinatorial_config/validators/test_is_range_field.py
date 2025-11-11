"""Tests for is_range_field validator."""

from combinatorial_config.validators import is_range_field


class TestIsRangeField:
    def test_valid_length_1(self):
        assert is_range_field((5,)) is True
        assert is_range_field((10.5,)) is True

    def test_valid_length_2(self):
        assert is_range_field((1, 10)) is True
        assert is_range_field((0.0, 1.0)) is True

    def test_valid_length_3(self):
        assert is_range_field((1, 10, 2)) is True
        assert is_range_field((0.0, 1.0, 0.1)) is True

    def test_invalid_length(self):
        assert is_range_field(()) is False
        assert is_range_field((1, 2, 3, 4)) is False

    def test_invalid_type(self):
        assert is_range_field([1, 2]) is False
        assert is_range_field("(1, 2)") is False

    def test_invalid_element_type(self):
        assert is_range_field(("a",)) is False
        assert is_range_field((1, "b")) is False
