"""Tests for is_number_value validator."""

from combinatorial_config.validators import is_number_value


class TestIsNumberValue:
    def test_valid_int(self):
        assert is_number_value(1) is True
        assert is_number_value(0) is True
        assert is_number_value(-42) is True

    def test_valid_float(self):
        assert is_number_value(1.0) is True
        assert is_number_value(3.14) is True
        assert is_number_value(-0.5) is True

    def test_invalid(self):
        assert is_number_value("1") is False
        assert is_number_value(None) is False
        assert is_number_value([1, 2]) is False
        assert is_number_value({}) is False
