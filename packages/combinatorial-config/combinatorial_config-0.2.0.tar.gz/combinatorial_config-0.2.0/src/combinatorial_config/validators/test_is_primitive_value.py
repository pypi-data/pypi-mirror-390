"""Tests for is_primitive_value validator."""

from combinatorial_config.validators import is_primitive_value


class TestIsPrimitiveValue:
    def test_valid_numbers(self):
        assert is_primitive_value(1) is True
        assert is_primitive_value(3.14) is True

    def test_valid_str(self):
        assert is_primitive_value("foo") is True
        assert is_primitive_value("") is True

    def test_valid_bool(self):
        assert is_primitive_value(True) is True
        assert is_primitive_value(False) is True

    def test_invalid(self):
        assert is_primitive_value(None) is False
        assert is_primitive_value([1, 2]) is False
        assert is_primitive_value({}) is False
