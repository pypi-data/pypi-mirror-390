"""
test_generate_combinations
===========================

Comprehensive pytest test suite for the `generate_combinations` function.

This module provides end-to-end tests for combinatorial configuration generation,
validating that the function correctly generates all combinations from various
configuration structures including flat, nested, range fields, and mixed scenarios.

Test Strategy
-------------
The test suite is organized into multiple test classes, each targeting specific
functionality:

1. **TestBasicCombinations**: Basic flat configurations with list/tuple values
2. **TestRangeFields**: Range field normalization and combination generation
3. **TestNestedFields**: Recursive nested combinatorial object handling
4. **TestMixedFields**: Mixed range, enum, and nested field scenarios
5. **TestExceptFields**: Field exclusion functionality
6. **TestEdgeCases**: Empty configs, single fields, dataclass support
7. **TestErrorCases**: Invalid input handling and error messages

Test Coverage
-------------
- Basic combination generation from flat configs
- Range field normalization (1, 2, 3-tuple formats)
- Nested combinatorial object recursive processing
- Mixed field types (range + enum + nested)
- Field exclusion via except_fields parameter
- Empty and single-field configurations
- Dataclass instance support
- Error handling for invalid inputs
- Enumerable value validation

Key Validation Rules Tested
----------------------------
1. All combinations are generated correctly (Cartesian product)
2. Range fields are normalized to lists before combination
3. Nested fields are processed recursively
4. Excluded fields are not included in combinations
5. All generated values are enumerable (primitives or Undefined)
6. Invalid configs raise appropriate errors

Examples
--------
Running the full test suite:

    $ pytest test_generate_combinations.py -v

Running a specific test class:

    $ pytest test_generate_combinations.py::TestBasicCombinations -v

See Also
--------
combinatorial_config.generate_combinations
    The function being tested.
"""

from dataclasses import dataclass
from combinatorial_config.generate_combinations import generate_combinations
from combinatorial_config.validators import is_combinatorial_object
from combinatorial_config.schemas import Undefined


class TestBasicCombinations:
    """Test basic combination generation from flat configurations."""

    def test_simple_two_fields(self):
        """Test basic two-field combination."""
        config = {
            "learning_rate": [0.1, 0.01],
            "batch_size": [16, 32],
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 4
        assert {"learning_rate": 0.1, "batch_size": 16} in combinations
        assert {"learning_rate": 0.1, "batch_size": 32} in combinations
        assert {"learning_rate": 0.01, "batch_size": 16} in combinations
        assert {"learning_rate": 0.01, "batch_size": 32} in combinations

    def test_three_fields(self):
        """Test three-field combination."""
        config = {
            "learning_rate": [0.1, 0.01],
            "batch_size": [16, 32],
            "dropout": [0.1, 0.2],
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 8  # 2 * 2 * 2

    def test_single_field(self):
        """Test single field configuration."""
        config = {"epochs": [10, 20, 30]}
        combinations = list(generate_combinations(config))
        assert len(combinations) == 3
        assert {"epochs": 10} in combinations
        assert {"epochs": 20} in combinations
        assert {"epochs": 30} in combinations

    def test_tuple_values(self):
        """Test configuration with tuple values."""
        config = {
            "optimizer": ("adam", "sgd"),
            "activation": ("relu", "tanh"),
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 4
        assert {"optimizer": "adam", "activation": "relu"} in combinations

    def test_mixed_types(self):
        """Test configuration with mixed value types."""
        config = {
            "epochs": [10, 20],
            "use_batch_norm": [True, False],
            "model_name": ["resnet", "vgg"],
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 8  # 2 * 2 * 2


class TestRangeFields:
    """Test range field normalization and combination generation."""

    def test_range_field_one_arg(self):
        """Test range field with single argument (stop)."""
        config = {"epochs": (5,), "optimizer": ["adam", "sgd"]}
        combinations = list(generate_combinations(config))
        # (5,) -> [0, 1, 2, 3, 4] -> 5 values
        assert len(combinations) == 10  # 5 * 2
        assert {"epochs": 0, "optimizer": "adam"} in combinations
        assert {"epochs": 4, "optimizer": "sgd"} in combinations

    def test_range_field_two_args(self):
        """Test range field with two arguments (start, stop)."""
        config = {"epochs": (2, 5), "optimizer": ["adam"]}
        combinations = list(generate_combinations(config))
        # (2, 5) -> [2, 3, 4] -> 3 values
        assert len(combinations) == 3
        assert {"epochs": 2, "optimizer": "adam"} in combinations
        assert {"epochs": 4, "optimizer": "adam"} in combinations

    def test_range_field_three_args(self):
        """Test range field with three arguments (start, stop, step)."""
        config = {"epochs": (0, 10, 2), "optimizer": ["adam"]}
        combinations = list(generate_combinations(config))
        # (0, 10, 2) -> [0, 2, 4, 6, 8] -> 5 values
        assert len(combinations) == 5
        assert {"epochs": 0, "optimizer": "adam"} in combinations
        assert {"epochs": 8, "optimizer": "adam"} in combinations

    def test_range_field_float(self):
        """Test range field with float values."""
        config = {"learning_rate": (0.0, 0.3, 0.1), "epochs": [10]}
        combinations = list(generate_combinations(config))
        # (0.0, 0.3, 0.1) -> [0.0, 0.1, 0.2] -> 3 values
        assert len(combinations) == 3
        assert {"learning_rate": 0.0, "epochs": 10} in combinations
        assert {"learning_rate": 0.2, "epochs": 10} in combinations

    def test_multiple_range_fields(self):
        """Test multiple range fields."""
        config = {
            "epochs": (0, 3),
            "layers": (2, 5),
        }
        combinations = list(generate_combinations(config))
        # epochs: [0, 1, 2] (3), layers: [2, 3, 4] (3) -> 9 combinations
        assert len(combinations) == 9


class TestNestedFields:
    """Test recursive nested combinatorial object handling."""

    def test_simple_nested(self):
        """Test simple nested configuration."""
        config = {
            "model": {"layers": [2, 4], "activation": ["relu", "tanh"]},
            "training": {"learning_rate": [0.1, 0.01]},
        }
        combinations = list(generate_combinations(config))
        # model: 2 * 2 = 4, training: 2 -> total: 4 * 2 = 8
        assert len(combinations) == 8
        assert all("model" in combo and "training" in combo for combo in combinations)
        assert all(
            isinstance(combo["model"], dict) and isinstance(combo["training"], dict)
            for combo in combinations
        )

    def test_deeply_nested(self):
        """Test deeply nested configuration."""
        config = {
            "model": {
                "backbone": {"type": ["resnet", "vgg"]},
                "head": {"classes": [10, 100]},
            },
            "training": {"epochs": [10, 20]},
        }
        combinations = list(generate_combinations(config))
        # backbone: 2, head: 2, training: 2 -> total: 2 * 2 * 2 = 8
        assert len(combinations) == 8

    def test_nested_with_range(self):
        """Test nested configuration with range fields."""
        config = {
            "model": {"layers": (2, 5)},
            "training": {"epochs": (0, 3)},
        }
        combinations = list(generate_combinations(config))
        # model: [2, 3, 4] (3), training: [0, 1, 2] (3) -> 9
        assert len(combinations) == 9

    def test_multiple_nested_fields(self):
        """Test multiple nested fields at same level."""
        config = {
            "model": {"layers": [2, 4]},
            "optimizer": {"lr": [0.1, 0.01]},
            "training": {"epochs": [10, 20]},
        }
        combinations = list(generate_combinations(config))
        # model: 2, optimizer: 2, training: 2 -> 2 * 2 * 2 = 8
        assert len(combinations) == 8


class TestMixedFields:
    """Test mixed field types (range + enum + nested)."""

    def test_range_and_enum(self):
        """Test mix of range and enum fields."""
        config = {
            "epochs": (0, 3),
            "optimizer": ["adam", "sgd"],
            "model": {"layers": [2, 4]},
        }
        combinations = list(generate_combinations(config))
        # epochs: 3, optimizer: 2, model: 2 -> 3 * 2 * 2 = 12
        assert len(combinations) == 12
        assert all("epochs" in combo for combo in combinations)
        assert all("optimizer" in combo for combo in combinations)
        assert all("model" in combo for combo in combinations)

    def test_all_field_types(self):
        """Test all field types together."""
        config = {
            "epochs": (0, 2),  # RangeField: [0, 1]
            "optimizer": ["adam", "sgd"],  # EnumField
            "model": {"layers": [2, 4]},  # Nested
            "use_dropout": [True, False],  # EnumField
        }
        combinations = list(generate_combinations(config))
        # epochs: 2, optimizer: 2, model: 2, use_dropout: 2 -> 2 * 2 * 2 * 2 = 16
        assert len(combinations) == 16


class TestExceptFields:
    """Test field exclusion functionality."""

    def test_except_single_field(self):
        """Test excluding a single field."""
        config = {
            "learning_rate": [0.1, 0.01],
            "batch_size": [16, 32],
            "model_name": ["resnet", "vgg"],
        }
        combinations = list(
            generate_combinations(config, except_fields=("model_name",))
        )
        assert len(combinations) == 4  # 2 * 2
        assert all("model_name" not in combo for combo in combinations)
        assert all("learning_rate" in combo for combo in combinations)
        assert all("batch_size" in combo for combo in combinations)

    def test_except_multiple_fields(self):
        """Test excluding multiple fields."""
        config = {
            "learning_rate": [0.1, 0.01],
            "batch_size": [16, 32],
            "dropout": [0.1, 0.2],
            "model_name": ["resnet"],
        }
        combinations = list(
            generate_combinations(config, except_fields=("model_name", "dropout"))
        )
        assert len(combinations) == 4  # 2 * 2
        assert all("model_name" not in combo for combo in combinations)
        assert all("dropout" not in combo for combo in combinations)

    def test_except_nested_field(self):
        """Test excluding a nested field."""
        config = {
            "model": {"layers": [2, 4]},
            "training": {"epochs": [10, 20]},
            "optimizer": ["adam", "sgd"],
        }
        combinations = list(generate_combinations(config, except_fields=("model",)))
        assert len(combinations) == 4  # 2 * 2
        assert all("model" not in combo for combo in combinations)
        assert all("training" in combo for combo in combinations)

    def test_except_field_with_invalid_value(self):
        """Test that except_fields allows invalid values to be excluded."""
        # Config with scalar value that would normally be invalid
        config = {
            "learning_rate": [0.1, 0.01],
            "batch_size": [16, 32],
            "invalid_field": 42,  # Scalar value - invalid without except_fields
        }
        # Should work when invalid_field is excluded
        combinations = list(
            generate_combinations(config, except_fields=("invalid_field",))
        )
        assert len(combinations) == 4  # 2 * 2
        assert all("invalid_field" not in combo for combo in combinations)

    def test_except_field_with_string_value(self):
        """Test that except_fields allows string values to be excluded."""
        # Config with string value that would normally be invalid
        config = {
            "learning_rate": [0.1, 0.01],
            "batch_size": [16, 32],
            "name": "experiment",  # String value - invalid without except_fields
        }
        # Should work when name is excluded
        combinations = list(generate_combinations(config, except_fields=("name",)))
        assert len(combinations) == 4  # 2 * 2
        assert all("name" not in combo for combo in combinations)

    def test_except_fields_passed_to_validation(self):
        """Test that except_fields is passed to is_combinatorial_object."""
        # Config that would be invalid without except_fields
        config = {
            "valid_field": [1, 2],
            "invalid_scalar": 42,
            "invalid_string": "test",
        }
        # Should raise error without except_fields
        try:
            list(generate_combinations(config))
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

        # Should work with except_fields
        combinations = list(
            generate_combinations(
                config, except_fields=("invalid_scalar", "invalid_string")
            )
        )
        assert len(combinations) == 2
        assert all("invalid_scalar" not in combo for combo in combinations)
        assert all("invalid_string" not in combo for combo in combinations)

    def test_except_fields_recursive(self):
        """Test that except_fields works recursively in nested fields."""
        config = {
            "model": {
                "layers": [2, 4],
                "invalid_field": 42,  # Invalid scalar
            },
            "training": {"epochs": [10, 20]},
        }
        # Should work when invalid_field is excluded in nested structure
        # except_fields is passed recursively to nested generate_combinations calls
        # which also passes it to is_combinatorial_object validation
        combinations = list(
            generate_combinations(config, except_fields=("invalid_field",))
        )
        assert len(combinations) == 4  # 2 * 2
        # invalid_field should not appear in any nested model dict
        for combo in combinations:
            assert isinstance(combo["model"], dict)
            assert "invalid_field" not in combo["model"]
            assert "layers" in combo["model"]

    def test_except_all_fields(self):
        """Test excluding all fields results in empty combinations."""
        config = {
            "field1": [1, 2],
            "field2": [3, 4],
        }
        combinations = list(
            generate_combinations(config, except_fields=("field1", "field2"))
        )
        assert len(combinations) == 1
        assert combinations[0] == {}

    def test_except_nonexistent_field(self):
        """Test that excluding non-existent fields doesn't cause errors."""
        config = {
            "learning_rate": [0.1, 0.01],
            "batch_size": [16, 32],
        }
        # Excluding non-existent field should work fine
        combinations = list(
            generate_combinations(config, except_fields=("nonexistent",))
        )
        assert len(combinations) == 4  # 2 * 2

    def test_except_field_with_range(self):
        """Test excluding a range field."""
        config = {
            "epochs": (0, 3),  # RangeField: [0, 1, 2]
            "optimizer": ["adam", "sgd"],
            "dropout": [0.1, 0.2],
        }
        combinations = list(generate_combinations(config, except_fields=("epochs",)))
        assert len(combinations) == 4  # 2 * 2
        assert all("epochs" not in combo for combo in combinations)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_config(self):
        """Test empty configuration."""
        config = {}
        combinations = list(generate_combinations(config))
        assert len(combinations) == 1
        assert combinations[0] == {}

    def test_only_nested_fields(self):
        """Test configuration with only nested fields."""
        config = {
            "model": {"layers": [2, 4]},
            "training": {"epochs": [10, 20]},
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 4  # 2 * 2

    def test_only_target_fields(self):
        """Test configuration with only target fields (no nested)."""
        config = {
            "learning_rate": [0.1, 0.01],
            "batch_size": [16, 32],
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 4

    def test_single_value_lists(self):
        """Test configuration with single-value lists."""
        config = {
            "learning_rate": [0.1],
            "batch_size": [16],
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 1
        assert combinations[0] == {"learning_rate": 0.1, "batch_size": 16}

    def test_dataclass_config(self):
        """Test configuration using dataclass instance."""

        @dataclass
        class Config:
            learning_rate: list[float]
            batch_size: list[int]

        config = Config(learning_rate=[0.1, 0.01], batch_size=[16, 32])
        assert is_combinatorial_object(config)
        combinations = list(generate_combinations(config))
        assert len(combinations) == 4
        assert all(isinstance(combo, dict) for combo in combinations)

    def test_nested_dataclass(self):
        """Test nested dataclass configuration."""

        @dataclass
        class ModelConfig:
            layers: list[int]

        @dataclass
        class TrainingConfig:
            epochs: list[int]

        @dataclass
        class Config:
            model: ModelConfig
            training: TrainingConfig

        config = Config(
            model=ModelConfig(layers=[2, 4]),
            training=TrainingConfig(epochs=[10, 20]),
        )
        combinations = list(generate_combinations(config))
        assert len(combinations) == 4


class TestErrorCases:
    """Test error handling and validation."""

    def test_invalid_combinatorial_object(self):
        """Test error when config is not a valid combinatorial object."""
        config = {"learning_rate": 0.1}  # Scalar value, not iterable
        try:
            list(generate_combinations(config))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid combinatorial object" in str(e)

    def test_non_enumerable_value(self):
        """Test error when field contains non-enumerable value."""
        config = {"values": [[1, 2], [3, 4]]}  # List of lists, not enumerable
        try:
            list(generate_combinations(config))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "non-enumerable value" in str(e)

    def test_none_value(self):
        """Test error when field contains None value."""
        config = {"values": [1, None, 3]}
        try:
            list(generate_combinations(config))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "non-enumerable value" in str(e)

    def test_dict_value(self):
        """Test error when field contains dict value (not nested combinatorial)."""
        config = {"values": [{"a": 1}, {"b": 2}]}  # List of dicts, not enumerable
        try:
            list(generate_combinations(config))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "non-enumerable value" in str(e)


class TestUndefinedSupport:
    """Test Undefined sentinel value support."""

    def test_undefined_in_enum(self):
        """Test Undefined value in enum field."""
        config = {
            "optimizer": ["adam", "sgd", Undefined],
            "epochs": [10, 20],
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 6  # 3 * 2
        assert any(combo["optimizer"] is Undefined for combo in combinations)

    def test_undefined_with_range(self):
        """Test Undefined value with range field."""
        config = {
            "optimizer": ["adam", Undefined],
            "epochs": (0, 2),  # [0, 1]
        }
        combinations = list(generate_combinations(config))
        assert len(combinations) == 4  # 2 * 2
        assert any(combo["optimizer"] is Undefined for combo in combinations)

    def test_undefined_value_alias(self):
        """Test undefined_value_alias parameter."""
        config = {
            "optimizer": ["adam", "__undefined__"],
            "epochs": [10, 20],
        }
        combinations = list(
            generate_combinations(config, undefined_value_alias="__undefined__")
        )
        assert len(combinations) == 4  # 2 * 2
        assert any(combo["optimizer"] is Undefined for combo in combinations)
        assert any(combo["optimizer"] == "adam" for combo in combinations)
        # Verify alias is converted to Undefined
        for combo in combinations:
            if combo["optimizer"] is Undefined:
                assert combo["optimizer"] != "__undefined__"
                assert combo["optimizer"] is Undefined

    def test_undefined_value_alias_with_nested(self):
        """Test undefined_value_alias with nested combinatorial objects."""
        config = {
            "optimizer": ["adam", "__undefined__"],
            "nested": {
                "learning_rate": [0.1, "__undefined__"],
                "batch_size": [16, 32],
            },
        }
        combinations = list(
            generate_combinations(config, undefined_value_alias="__undefined__")
        )
        assert len(combinations) == 8  # 2 * 2 * 2
        # Check that alias is converted in top-level fields
        assert any(combo["optimizer"] is Undefined for combo in combinations)
        # Check that alias is converted in nested fields
        assert any(
            combo["nested"]["learning_rate"] is Undefined for combo in combinations
        )


class TestIteratorBehavior:
    """Test iterator/generator behavior."""

    def test_is_iterator(self):
        """Test that function returns an iterator."""
        config = {"values": [1, 2, 3]}
        result = generate_combinations(config)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_lazy_evaluation(self):
        """Test that combinations are generated lazily."""
        config = {
            "a": list(range(1000)),
            "b": list(range(1000)),
        }
        # Should not raise memory error even with large config
        gen = generate_combinations(config)
        first = next(gen)
        assert "a" in first and "b" in first

    def test_multiple_iterations(self):
        """Test that iterator can be consumed multiple times."""
        config = {"values": [1, 2]}
        gen1 = generate_combinations(config)
        gen2 = generate_combinations(config)
        assert list(gen1) == list(gen2)
