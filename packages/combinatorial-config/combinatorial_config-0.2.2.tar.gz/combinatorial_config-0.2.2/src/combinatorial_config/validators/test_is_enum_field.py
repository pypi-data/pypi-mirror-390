"""Tests for is_enum_field validator."""

from combinatorial_config.schemas import Undefined
from combinatorial_config.validators import is_enum_field


class TestIsEnumField:
    def test_valid_primitives(self):
        assert is_enum_field(("on", "off")) is True
        assert is_enum_field((1, 2, 3)) is True
        assert is_enum_field((True, False)) is True
        assert is_enum_field((1.0, 2.0)) is True

    def test_valid_with_undefined(self):
        assert is_enum_field(("yes", "no", Undefined)) is True
        assert is_enum_field((Undefined,)) is True

    def test_valid_single_element(self):
        assert is_enum_field(("single",)) is True
        assert is_enum_field((1,)) is True

    def test_invalid_empty(self):
        assert is_enum_field(()) is False

    def test_invalid_type(self):
        assert is_enum_field([]) is False
        assert is_enum_field(["on", "off"]) is False

    def test_invalid_element_type(self):
        assert is_enum_field((1, 2, None)) is False
        assert is_enum_field((1, [2])) is False
