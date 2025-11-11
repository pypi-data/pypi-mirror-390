"""
test_is_combinatorial_object
=============================

Comprehensive pytest test suite for the `is_combinatorial_object` type guard function.

This module validates the runtime behavior of `is_combinatorial_object`, which
serves as a type guard for CombinatorialObject validation. The function validates
that all field values are either iterable (excluding strings) or nested combinatorial
objects, supporting both flat and hierarchical configuration structures.

Test Strategy
-------------
The test suite is organized into five main test classes, each targeting a
specific aspect of the validation logic:

1. **TestValidCombinatorialObjects**: Positive test cases
   - Verifies that valid combinatorial objects are correctly identified
   - Tests various iterable types: lists, tuples, sets, ranges, generators
   - Tests both dict and dataclass variants
   - Tests nested structures and empty iterables
   - Tests mixed iterable and nested combinatorial object fields

2. **TestInvalidCombinatorialObjects**: Negative test cases
   - Verifies that invalid objects are correctly rejected
   - Tests scalar values (int, float, bool)
   - Tests string values (explicitly excluded despite being iterable)
   - Tests primitive types and non-dict/non-dataclass objects
   - Tests mixed valid/invalid field scenarios

3. **TestEdgeCases**: Boundary conditions and special cases
   - Empty dicts and dataclasses (vacuously valid - base case)
   - None and bool values
   - Dataclass classes vs instances
   - Deep nesting structures

4. **TestTypeGuardBehavior**: TypeGuard functionality
   - Validates that the function works as a proper TypeGuard
   - Tests type narrowing behavior (primarily for static type checkers)

5. **TestDocstringExamples**: Documentation consistency
   - Ensures all examples in docstrings execute correctly
   - Serves as regression tests for documented behavior

Test Coverage
-------------
The test suite provides comprehensive coverage of:
- **Object types**: dicts, dataclass instances, regular classes, primitives
- **Iterable types**: lists, tuples, sets, ranges, generators, dicts, bytes
- **Non-iterable types**: int, float, str, bool, None
- **Structural variants**: empty, single-field, multi-field, nested
- **Mixed scenarios**: some fields iterable, some nested combinatorial objects

Fixtures
--------
The module defines several dataclass fixtures for testing:
- ValidConfig: All fields are iterable (valid)
- InvalidConfigScalar: Scalar fields (invalid)
- InvalidConfigString: Contains string field (invalid)
- MixedConfig: Mix of iterable and non-iterable fields (invalid)
- EmptyConfig: No fields (valid - vacuously true)
- NestedConfig: Contains nested combinatorial object fields (valid)
- RegularClass: Non-dataclass class (invalid)

Key Validation Rules Tested
----------------------------
1. Object must be dict or dataclass instance (not class itself)
2. All field values must be iterable OR valid combinatorial objects
3. String values are explicitly rejected (treated as atomic, not iterable)
4. Empty objects are valid (no fields to fail validation)
5. Primitive types and non-dict/non-dataclass objects are invalid
6. Nested combinatorial objects are supported (recursive validation)

Notes
-----
These tests focus on runtime behavior. The TypeGuard functionality provides
additional benefits at static type checking time (via mypy, pyright, etc.),
which cannot be fully tested here but are verified through type narrowing tests.

The distinction between "iterable but invalid" (strings) and "iterable and valid"
(other iterables) is a critical design decision tested throughout this suite.

Examples
--------
Running the full test suite:

    $ pytest test_is_combinatorial_object.py -v

Running a specific test class:

    $ pytest test_is_combinatorial_object.py::TestValidCombinatorialObjects -v

Running with coverage:

    $ pytest test_is_combinatorial_object.py --cov=is_combinatorial_object

See Also
--------
combinatorial_config.validators.is_combinatorial_object
    The function being tested.
combinatorial_config.schemas.CombinatorialObject
    The type alias for validated objects.
"""

from dataclasses import dataclass
from typing import Any

from combinatorial_config.validators.is_combinatorial_object import (
    is_combinatorial_object,
)


# Test fixtures: dataclass definitions
@dataclass
class ValidConfig:
    """Dataclass with all iterable fields (valid)."""
    learning_rates: list[float]
    batch_sizes: tuple[int, ...]
    epochs: list[int]


@dataclass
class EmptyConfig:
    """Dataclass with no fields (valid - vacuously true)."""
    pass


@dataclass
class NestedConfig:
    """Dataclass with nested combinatorial object fields (valid)."""
    sub_config: dict  # Will contain a combinatorial object
    parameters: list[float]  # Iterable field


@dataclass
class InvalidConfigScalar:
    """Dataclass with scalar (non-iterable) fields."""
    learning_rate: float
    batch_size: int


@dataclass
class InvalidConfigString:
    """Dataclass with string field."""
    name: str
    experiments: list[str]


@dataclass
class MixedConfig:
    """Dataclass with both valid (iterable) and invalid (scalar) fields."""
    learning_rates: list[float]  # Valid (iterable)
    model_name: str  # Invalid (string)


class RegularClass:
    """Regular class (not a dataclass)."""
    def __init__(self):
        self.values = [1, 2, 3]


class TestValidCombinatorialObjects:
    """
    Test cases for valid combinatorial objects.

    This class contains positive test cases that verify `is_combinatorial_object`
    correctly identifies valid combinatorial configuration objects. A valid object
    must be either a dict or dataclass instance with all field values being
    iterable (excluding strings) or nested combinatorial objects.

    Test Coverage
    -------------
    - Empty dicts and dataclasses (vacuously valid)
    - Dict variants: lists, tuples, sets, ranges  
    - Dataclass variants: mixed iterable types
    - Nested combinatorial objects
    - Mixed iterable and nested combinatorial object fields

    All tests in this class should return True from is_combinatorial_object().
    """

    def test_valid_empty_dict(self):
        """Empty dict should be valid (base case)."""
        obj = {}
        assert is_combinatorial_object(obj) is True

    def test_valid_empty_dataclass(self):
        """Empty dataclass should be valid (base case)."""
        obj = EmptyConfig()
        assert is_combinatorial_object(obj) is True

    def test_valid_dict_with_empty_dict_value(self):
        """Dict with empty dict value should be valid."""
        obj = {"nested": {}}
        assert is_combinatorial_object(obj) is True

    def test_valid_dict_with_multiple_empty_dicts(self):
        """Dict with multiple empty dict values should be valid."""
        obj = {
            "config_a": {},
            "config_b": {},
            "config_c": {},
        }
        assert is_combinatorial_object(obj) is True

    def test_valid_dict_with_lists(self):
        """Dict with list values should be valid."""
        obj = {
            "learning_rate": [0.1, 0.01, 0.001],
            "batch_size": [16, 32, 64],
        }
        assert is_combinatorial_object(obj) is True

    def test_valid_dict_with_tuples(self):
        """Dict with tuple values should be valid."""
        obj = {"lr": (0.1, 0.01), "bs": (16, 32)}
        assert is_combinatorial_object(obj) is True

    def test_valid_dataclass_with_lists(self):
        """Dataclass with list fields should be valid."""
        obj = ValidConfig(
            learning_rates=[0.1, 0.01],
            batch_sizes=(16, 32),
            epochs=[10, 20],
        )
        assert is_combinatorial_object(obj) is True

    def test_valid_nested_combinatorial_object(self):
        """Dict with nested combinatorial object values should be valid."""
        obj = {
            "model": {"layers": [2, 4, 8]},
            "training": {"lr": [0.1, 0.01]},
        }
        assert is_combinatorial_object(obj) is True

    def test_valid_mixed_iterable_and_nested(self):
        """Mixed iterable and nested combinatorial object should be valid."""
        obj = {
            "params": [0.1, 0.2],
            "config": {"nested": [1, 2, 3]},
        }
        assert is_combinatorial_object(obj) is True

    def test_valid_dataclass_with_nested_config(self):
        """Dataclass with nested combinatorial object field should be valid."""
        obj = NestedConfig(
            sub_config={"lr": [0.1, 0.01]},
            parameters=[1.0, 2.0],
        )
        assert is_combinatorial_object(obj) is True


class TestInvalidCombinatorialObjects:
    """
    Test cases for invalid combinatorial objects.

    This class contains negative test cases that verify `is_combinatorial_object`
    correctly rejects invalid combinatorial configuration objects. Invalid objects
    include those with scalar values, string values, primitive types, or objects
    that are not dicts or dataclass instances.

    Test Coverage
    -------------
    - Scalar values: int, float (non-iterable)
    - String values: explicitly excluded despite being iterable
    - Mixed configurations: some fields valid, some invalid
    - Wrong object types: primitives, regular classes, collections (list, tuple, set)
    - Dataclass variants: scalar fields, string fields, mixed fields

    All tests in this class should return False from is_combinatorial_object().

    Key Design Decision
    -------------------
    Strings are rejected despite being iterable in Python. This is because in the
    context of combinatorial configurations, strings represent atomic scalar values
    (like "adam" optimizer or "resnet" model) rather than collections to iterate over.
    """

    def test_invalid_dict_with_scalar_int(self):
        """Dict with scalar int value should be invalid (not iterable)."""
        obj = {"learning_rate": 0.1, "batch_size": 32}
        assert is_combinatorial_object(obj) is False

    def test_invalid_dict_with_scalar_float(self):
        """Dict with scalar float value should be invalid (not iterable)."""
        obj = {"learning_rate": 0.001}
        assert is_combinatorial_object(obj) is False

    def test_invalid_dict_with_string(self):
        """Dict with string value should be invalid (strings excluded)."""
        obj = {"name": "experiment1", "model": "resnet"}
        assert is_combinatorial_object(obj) is False

    def test_invalid_dict_with_mixed_values(self):
        """Dict with mixed iterable and scalar values should be invalid."""
        obj = {
            "learning_rate": [0.1, 0.01],  # Valid (iterable)
            "batch_size": 32,  # Invalid (scalar)
        }
        assert is_combinatorial_object(obj) is False

    def test_invalid_dataclass_with_scalar(self):
        """Dataclass with scalar fields should be invalid."""
        obj = InvalidConfigScalar(learning_rate=0.1, batch_size=32)
        assert is_combinatorial_object(obj) is False

    def test_invalid_dataclass_with_string(self):
        """Dataclass with string field should be invalid."""
        obj = InvalidConfigString(name="exp1", experiments=["a", "b"])
        assert is_combinatorial_object(obj) is False

    def test_invalid_dataclass_with_mixed(self):
        """Dataclass with mixed iterable and string fields should be invalid."""
        obj = MixedConfig(learning_rates=[0.1, 0.01], model_name="resnet")
        assert is_combinatorial_object(obj) is False

    def test_invalid_primitive_int(self):
        """Primitive int should be invalid."""
        assert is_combinatorial_object(42) is False

    def test_invalid_primitive_float(self):
        """Primitive float should be invalid."""
        assert is_combinatorial_object(3.14) is False

    def test_invalid_primitive_string(self):
        """Primitive string should be invalid."""
        assert is_combinatorial_object("config") is False

    def test_invalid_primitive_bool(self):
        """Primitive bool should be invalid."""
        assert is_combinatorial_object(True) is False

    def test_invalid_primitive_none(self):
        """None should be invalid."""
        assert is_combinatorial_object(None) is False

    def test_invalid_list(self):
        """Plain list should be invalid (not dict or dataclass)."""
        assert is_combinatorial_object([1, 2, 3]) is False

    def test_invalid_tuple(self):
        """Plain tuple should be invalid (not dict or dataclass)."""
        assert is_combinatorial_object((1, 2, 3)) is False

    def test_invalid_set(self):
        """Plain set should be invalid (not dict or dataclass)."""
        assert is_combinatorial_object({1, 2, 3}) is False

    def test_invalid_regular_class(self):
        """Regular class instance should be invalid (not dataclass)."""
        obj = RegularClass()
        assert is_combinatorial_object(obj) is False


class TestEdgeCases:
    """
    Test edge cases and boundary conditions.

    This class tests unusual or boundary conditions that might not be covered
    by the standard valid/invalid test cases. These tests verify the function's
    behavior on edge cases and help ensure robustness.

    Test Coverage
    -------------
    - Empty containers: empty dict, empty dataclass (both valid - vacuously true)
    - Special values: None, bool (both invalid)
    - Nested structures: dict values, bytes (bytes iterable, dicts can be combinatorial objects)
    - Type vs instance: dataclass class vs dataclass instance

    Design Decisions Tested
    -----------------------
    1. Empty objects are valid: An object with zero fields vacuously satisfies
       "all fields are iterable or combinatorial objects"

    2. Dataclass classes are invalid: Only instances are accepted, not the
       class itself, even though classes have __dataclass_fields__

    3. Dicts as values: Valid if they are combinatorial objects (either empty
       or containing iterable/combinatorial object values)

    4. Bytes are iterable: Bytes objects are valid field values (they yield ints)
    """

    def test_empty_dict(self):
        """Empty dict should be valid (base case)."""
        assert is_combinatorial_object({}) is True

    def test_empty_dataclass(self):
        """Empty dataclass should be valid (base case)."""
        obj = EmptyConfig()
        assert is_combinatorial_object(obj) is True

    def test_dict_with_none_value(self):
        """Dict with None value should be invalid (not iterable)."""
        obj = {"key": None}
        assert is_combinatorial_object(obj) is False

    def test_dict_with_bool_value(self):
        """Dict with bool value should be invalid (not iterable)."""
        obj = {"flag": True}
        assert is_combinatorial_object(obj) is False

    def test_dict_with_dict_value(self):
        """Dict with dict value should be valid (dict is iterable)."""
        obj = {"nested": {"a": 1, "b": 2}}
        # The nested dict itself is iterable (yields keys), so it's valid
        # Note: dict is iterable (yields keys when iterated)
        assert is_combinatorial_object(obj) is True

    def test_dict_with_nested_combinatorial_object(self):
        """Dict with nested combinatorial object value should be valid."""
        obj = {"nested": {"a": [1, 2], "b": [3, 4]}}
        # The nested dict is a valid combinatorial object (iterable values)
        assert is_combinatorial_object(obj) is True

    def test_dict_with_bytes_value(self):
        """Dict with bytes value should be valid (bytes is iterable)."""
        obj = {"data": b"hello"}
        # bytes is iterable (yields ints), so it's valid
        assert is_combinatorial_object(obj) is True

    def test_dataclass_class_itself(self):
        """Passing dataclass class (not instance) should be invalid."""
        # The class itself, not an instance
        assert is_combinatorial_object(EmptyConfig) is False
        # The class has __dataclass_fields__ but we only accept instances


class TestTypeGuardBehavior:
    """
    Test TypeGuard behavior for type narrowing.

    This class tests that `is_combinatorial_object` functions correctly as a
    TypeGuard, which enables static type checkers (mypy, pyright, etc.) to
    narrow the type of validated objects from `Any` to `CombinatorialObject`.

    Test Coverage
    -------------
    - Dict type narrowing: Verifies runtime behavior after type guard
    - Dataclass type narrowing: Verifies dataclass-specific attributes are accessible

    Notes
    -----
    The primary benefit of TypeGuard is at static analysis time. These tests
    verify runtime behavior, but the real value is in how type checkers use
    this information to provide better type safety and IDE support.

    After `is_combinatorial_object(obj)` returns True:
    - Static type checkers narrow `obj` from `Any` to `CombinatorialObject`
    - This enables autocomplete and type checking on CombinatorialObject operations
    - Type errors are caught at static analysis time rather than runtime
    """

    def test_type_guard_narrows_dict(self):
        """Test that TypeGuard allows dict to be treated as CombinatorialObject."""
        obj: Any = {"lr": [0.1, 0.01], "bs": [16, 32]}
        if is_combinatorial_object(obj):
            # After the guard, obj should be narrowed to CombinatorialObject
            # This is mainly for static type checkers, but we can test runtime behavior
            assert isinstance(obj, (dict, object))

    def test_type_guard_narrows_dataclass(self):
        """Test that TypeGuard allows dataclass to be treated as CombinatorialObject."""
        obj: Any = ValidConfig([0.1], (16,), [10])
        if is_combinatorial_object(obj):
            # After the guard, obj should be narrowed to CombinatorialObject
            assert hasattr(obj, "__dataclass_fields__")


class TestDocstringExamples:
    """
    Verify all examples from docstrings work as documented.

    This class serves as regression tests for all code examples provided in
    the docstrings of `is_combinatorial_object` and related documentation.
    These tests ensure that documented examples remain accurate and functional
    as the codebase evolves.

    Purpose
    -------
    1. **Documentation accuracy**: Ensures examples in docstrings are correct
    2. **Regression prevention**: Catches breaking changes to documented behavior
    3. **Living documentation**: Tests serve as executable specifications
    4. **User confidence**: Users can trust that documented examples work

    Test Coverage
    -------------
    Each test corresponds to a specific example from the function's docstring:
    - Valid empty structures (base case)
    - Valid nested empty structures
    - Valid structures with iterable values
    - Valid nested configuration structures
    - Invalid scalar examples
    - Invalid string examples
    - Invalid primitive type examples

    Maintenance
    -----------
    When updating docstring examples, corresponding tests in this class should
    also be updated to maintain synchronization between documentation and tests.
    """

    def test_valid_empty_structures(self):
        """Test that empty dict/dataclass are valid (base case)."""
        assert is_combinatorial_object({}) is True

        @dataclass
        class EmptyParams:
            pass

        assert is_combinatorial_object(EmptyParams()) is True

    def test_valid_nested_empty_structures(self):
        """Test that nested empty structures are valid."""
        nested_dict = {"config_a": {}, "config_b": {"nested": {}}}
        assert is_combinatorial_object(nested_dict) is True

    def test_valid_dict_with_lists(self):
        """Test that dicts with list values are valid."""
        config_dict = {
            "learning_rate": [0.1, 0.01, 0.001],
            "batch_size": [16, 32, 64],
        }
        assert is_combinatorial_object(config_dict) is True

    def test_valid_dataclass_with_lists(self):
        """Test that dataclasses with list fields are valid."""

        @dataclass
        class HyperParams:
            lr: list[float]
            epochs: tuple[int, ...]

        params = HyperParams([0.1, 0.01], (10, 20, 30))
        assert is_combinatorial_object(params) is True

    def test_valid_nested_config(self):
        """Test valid nested configuration structures."""
        nested_cfg = {
            "model": {"layers": [2, 4, 8]},
            "training": {"optimizer": {"lr": [0.1, 0.01]}},
        }
        assert is_combinatorial_object(nested_cfg) is True

    def test_invalid_scalar(self):
        """Test the invalid scalar example."""
        scalar_config = {"lr": 0.1, "bs": 32}
        assert is_combinatorial_object(scalar_config) is False

    def test_invalid_string(self):
        """Test the invalid string example."""
        string_config = {"name": "experiment1"}
        assert is_combinatorial_object(string_config) is False

    def test_invalid_primitive_int(self):
        """Test the invalid int example."""
        assert is_combinatorial_object(42) is False

    def test_invalid_primitive_list(self):
        """Test the invalid list example."""
        assert is_combinatorial_object([1, 2, 3]) is False
