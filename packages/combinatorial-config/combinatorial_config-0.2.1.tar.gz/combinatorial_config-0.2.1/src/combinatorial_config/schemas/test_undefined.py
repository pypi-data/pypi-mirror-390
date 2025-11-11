"""Tests for Undefined sentinel value."""

from combinatorial_config.schemas import Undefined, _UndefinedType


class TestUndefined:
    def test_singleton(self):
        assert Undefined is _UndefinedType()
        assert Undefined is Undefined

    def test_repr(self):
        assert repr(Undefined) == "Undefined"

    def test_bool(self):
        assert bool(Undefined) is False

    def test_identity(self):
        assert Undefined is not None
        assert Undefined is not False
        assert Undefined is not True
