"""Tests for is_enumerable_value validator."""

from combinatorial_config.schemas import Undefined
from combinatorial_config.validators import is_enumerable_value


class TestIsEnumerableValue:
    def test_valid_primitives(self):
        assert is_enumerable_value(1) is True
        assert is_enumerable_value(3.14) is True
        assert is_enumerable_value("foo") is True
        assert is_enumerable_value(True) is True

    def test_valid_undefined(self):
        assert is_enumerable_value(Undefined) is True

    def test_invalid(self):
        assert is_enumerable_value(None) is False
        assert is_enumerable_value([1, 2]) is False
        assert is_enumerable_value({}) is False
