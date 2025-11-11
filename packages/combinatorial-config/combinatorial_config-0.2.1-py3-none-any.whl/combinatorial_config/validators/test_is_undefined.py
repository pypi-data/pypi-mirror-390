"""Tests for is_undefined validator."""

from combinatorial_config.schemas import Undefined
from combinatorial_config.validators import is_undefined


class TestIsUndefined:
    def test_valid(self):
        assert is_undefined(Undefined) is True

    def test_invalid(self):
        assert is_undefined(None) is False
        assert is_undefined(False) is False
        assert is_undefined("") is False
        assert is_undefined(0) is False
