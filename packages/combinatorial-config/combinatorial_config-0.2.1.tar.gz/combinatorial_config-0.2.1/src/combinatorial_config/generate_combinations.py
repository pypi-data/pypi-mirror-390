# TODO: optional field를 지원해야함. (Undefined인 경우, 실현된 조합이 hasattr에서 False를 반환해야함.)
# TODO: exceptional field를 지원해야함. (지정된 몇몇 필드는 callback 함수를 통해 처리되어야함, 또는 지정된 필드를 그대로 반환하도록 처리해야함. (개발자/사용자가 그대로 처리할 수 있도록))
#
# 구현 완료된 기능:
# - nested field 지원: 재귀적으로 nested combinatorial object를 처리하여 모든 조합을 생성함
# - undefined_value_alias: 지정된 값을 Undefined sentinel로 변환하는 기능

import itertools
from dataclasses import asdict
from typing import Tuple, Iterator, Any, Optional, cast
from .schemas import CombinatorialObject, Undefined
from .validators import (
    is_combinatorial_object,
    is_range_field,
    is_enumerable_value,
)
from .normalizers import Range


def generate_combinations(
    config: CombinatorialObject,
    except_fields: Tuple[str, ...] = tuple(),
    undefined_value_alias: Optional[Any] = None,
) -> Iterator[CombinatorialObject]:
    """
    Generate all combinations from a combinatorial configuration object.

    This function recursively processes nested combinatorial objects and generates
    all possible combinations of field values. Range fields are normalized and
    converted to lists, and all field values are validated to be enumerable.

    The function supports:
    - Flat configurations with iterable field values (lists, tuples, ranges)
    - Nested hierarchical configurations with combinatorial objects as field values
    - Range fields that are automatically normalized to lists
    - Optional undefined value aliases that are converted to Undefined sentinel
    - Field exclusion via except_fields parameter

    Parameters
    ----------
    config : CombinatorialObject
        A combinatorial configuration object (dict or dataclass) where field
        values are iterables or nested combinatorial objects. All field values
        must be iterable (excluding strings) or valid combinatorial objects.
    except_fields : Tuple[str, ...], optional
        Field names to exclude from combination generation. These fields are
        excluded from both validation and combination generation. Works
        recursively for nested structures. Default is empty tuple.
    undefined_value_alias : Any, optional
        A value that should be treated as Undefined in the generated combinations.
        If provided, any occurrence of this value in the combinations (including
        nested structures) will be replaced with the Undefined sentinel value.
        This allows using custom values (e.g., strings like "__undefined__") as
        placeholders that get converted to the proper Undefined sentinel.
        Default is None (no alias conversion).

    Yields
    ------
    CombinatorialObject
        Each generated combination as a dictionary. Nested combinatorial objects
        are included as nested dictionaries. Values matching undefined_value_alias
        are replaced with Undefined sentinel.

    Raises
    ------
    ValueError
        If config is not a valid combinatorial object, or if any field value
        is not enumerable after normalization.

    Notes
    -----
    - Nested combinatorial objects are processed recursively, generating all
      combinations for each nested structure independently and then combining
      them with the parent level combinations.
    - Range fields (tuples of 1-3 numbers) are automatically normalized to
      lists before combination generation.
    - The undefined_value_alias conversion applies to all levels of nesting
      when recursively processing nested structures.
    - Empty configurations yield a single empty dictionary.

    Examples
    --------
    **Example 1: Basic flat configuration**

    Generate all combinations from a simple flat configuration with list values:

    >>> config = {
    ...     "learning_rate": [0.1, 0.01],
    ...     "batch_size": [16, 32]
    ... }
    >>> combinations = list(generate_combinations(config))
    >>> len(combinations)
    4
    >>> combinations[0]
    {'learning_rate': 0.1, 'batch_size': 16}
    >>> combinations[1]
    {'learning_rate': 0.1, 'batch_size': 32}
    >>> combinations[2]
    {'learning_rate': 0.01, 'batch_size': 16}
    >>> combinations[3]
    {'learning_rate': 0.01, 'batch_size': 32}

    **Example 2: Configuration with range fields**

    Range fields (tuples) are automatically normalized to lists before combination:

    >>> config_with_range = {
    ...     "epochs": (0, 3),  # RangeField: generates [0, 1, 2]
    ...     "optimizer": ["adam", "sgd"]
    ... }
    >>> combinations = list(generate_combinations(config_with_range))
    >>> len(combinations)  # 3 epochs × 2 optimizers = 6 combinations
    6
    >>> combinations
    [{'epochs': 0, 'optimizer': 'adam'}, {'epochs': 0, 'optimizer': 'sgd'}, {'epochs': 1, 'optimizer': 'adam'}, {'epochs': 1, 'optimizer': 'sgd'}, {'epochs': 2, 'optimizer': 'adam'}, {'epochs': 2, 'optimizer': 'sgd'}]

    **Example 3: Nested hierarchical configuration**

    Nested combinatorial objects are processed recursively, generating all combinations
    for each nested structure and then combining them:

    >>> nested_config = {
    ...     "model": {"layers": [2, 4], "activation": ["relu", "tanh"]},
    ...     "training": {"epochs": [10, 20], "optimizer": ["adam"]}
    ... }
    >>> combinations = list(generate_combinations(nested_config))
    >>> len(combinations)  # model: 2×2=4, training: 2×1=2 → total: 4×2=8
    8
    >>> combinations[0]
    {'model': {'layers': 2, 'activation': 'relu'}, 'training': {'epochs': 10, 'optimizer': 'adam'}}
    >>> combinations[1]
    {'model': {'layers': 2, 'activation': 'relu'}, 'training': {'epochs': 20, 'optimizer': 'adam'}}
    >>> combinations[2]
    {'model': {'layers': 2, 'activation': 'tanh'}, 'training': {'epochs': 10, 'optimizer': 'adam'}}

    **Example 4: Using undefined_value_alias**

    Convert custom placeholder values to Undefined sentinel:

    >>> from combinatorial_config.schemas import Undefined
    >>> config_with_alias = {
    ...     "optimizer": ["adam", "__undefined__"],
    ...     "epochs": [10, 20]
    ... }
    >>> combinations = list(generate_combinations(config_with_alias, undefined_value_alias="__undefined__"))
    >>> len(combinations)
    4
    >>> # Check that alias was converted to Undefined
    >>> combinations[1]["optimizer"] is Undefined
    True
    >>> combinations[0]["optimizer"]
    'adam'
    >>> # Works in nested structures too
    >>> nested_with_alias = {
    ...     "model": {"type": ["resnet", "__undefined__"]},
    ...     "epochs": [10, 20]
    ... }
    >>> nested_combos = list(generate_combinations(nested_with_alias, undefined_value_alias="__undefined__"))
    >>> nested_combos[1]["model"]["type"] is Undefined
    True

    **Example 5: Excluding fields**

    Exclude fields from combination generation (useful for invalid or metadata fields):

    >>> config = {
    ...     "learning_rate": [0.1, 0.01],
    ...     "batch_size": [16, 32],
    ...     "debug_mode": True  # Invalid: not iterable, but can be excluded
    ... }
    >>> combinations = list(generate_combinations(config, except_fields=("debug_mode",)))
    >>> len(combinations)
    4
    >>> all("debug_mode" not in combo for combo in combinations)
    True
    >>> combinations[0]
    {'learning_rate': 0.1, 'batch_size': 16}

    **Example 6: Empty configuration**

    Empty configurations yield a single empty dictionary:

    >>> list(generate_combinations({}))
    [{}]
    """
    if not is_combinatorial_object(config, except_fields):
        raise ValueError("Invalid combinatorial object")

    # Convert dataclass to dict for uniform processing
    config_dict = config if isinstance(config, dict) else asdict(cast(Any, config))

    # Step 1: Classify fields into nested and target fields
    all_fields = tuple(config_dict.keys())
    candidate_fields = tuple(set(all_fields) - set(except_fields))

    nested_fields = tuple(
        key
        for key in candidate_fields
        if is_combinatorial_object(config_dict.get(key), except_fields)
    )

    target_fields = tuple(set(candidate_fields) - set(nested_fields))

    # Step 2: Normalize and validate target fields
    normalized_values = {}
    for field_name in target_fields:
        value = config_dict[field_name]

        # Normalize range fields (tuples) to lists
        if is_range_field(value):
            normalized_list = Range.to_list(value)
        else:
            # Already a list/iterable, convert to list for validation
            normalized_list = list(value)

        # Validate all values are enumerable (primitives or Undefined)
        for item in normalized_list:
            if not is_enumerable_value(item):
                raise ValueError(
                    f"Field '{field_name}' contains non-enumerable value: {item}"
                )

        normalized_values[field_name] = normalized_list
    field_names = list(normalized_values.keys())

    # Step 3: Generate combinations for nested fields recursively
    nested_combinations = []
    for nested_field in nested_fields:
        nested_config = config_dict[nested_field]
        nested_combs = list(
            generate_combinations(nested_config, except_fields, undefined_value_alias)
        )
        nested_combinations.append((nested_field, nested_combs))

    # Step 4: Generate and yield combinations
    if not field_names:
        # Case 1: Only nested fields (or empty config)
        if not nested_combinations:
            # Empty config, yield empty dict
            yield {}
            return

        # Extract field names and value lists for product
        nested_field_names = [name for name, _ in nested_combinations]
        nested_value_lists = [combs for _, combs in nested_combinations]

        for nested_combo in itertools.product(*nested_value_lists):
            result = {}
            for field_name, nested_result in zip(nested_field_names, nested_combo):
                # nested_result is already a dict from recursive call
                result[field_name] = nested_result
            yield result
    else:
        # Case 2 & 3: Target fields (with optional nested fields)
        value_lists = [normalized_values[name] for name in field_names]

        for target_combo in itertools.product(*value_lists):
            # Build result from target field values
            result = {}
            for field_name, value in zip(field_names, target_combo):
                # Convert undefined_value_alias to Undefined if it matches
                if undefined_value_alias is not None and value == undefined_value_alias:
                    value = Undefined
                result[field_name] = value

            # Combine with nested field combinations if they exist
            if nested_combinations:
                nested_field_names = [name for name, _ in nested_combinations]
                nested_value_lists = [combs for _, combs in nested_combinations]

                for nested_combo in itertools.product(*nested_value_lists):
                    combined_result = result.copy()
                    for field_name, nested_result in zip(
                        nested_field_names, nested_combo
                    ):
                        # nested_result is already a dict from recursive call
                        combined_result[field_name] = nested_result
                    yield combined_result
            else:
                # Only target fields, no nested structures
                yield result
