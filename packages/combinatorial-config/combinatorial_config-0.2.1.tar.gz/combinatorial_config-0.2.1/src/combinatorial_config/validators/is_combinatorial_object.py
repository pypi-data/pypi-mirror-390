"""
is_combinatorial_object
=======================

Type guard for validating combinatorial configuration objects.

This module provides runtime validation for objects that can be used as
combinatorial configurations. A valid combinatorial object must be either a
dict or a dataclass instance where all field values are iterable (excluding
strings) or nested combinatorial objects, supporting both flat and hierarchical
structures.

Functions
---------
is_combinatorial_object
    Type guard function that validates whether an object satisfies the
    CombinatorialObject requirements and narrows the type accordingly.

Notes
-----
The validation enforces that:
1. The object must be either a dict or a dataclass instance (not a class)
2. All field values must be either:
   - Iterable (list, tuple, set, range, etc.) - excluding strings
   - Valid combinatorial objects (for nested structures)

This allows both flat configurations with iterable values and hierarchical
nested configurations. String values are explicitly rejected despite being
iterable, as they represent atomic scalar values in the context of combinatorial
configurations.

The recursive validation for nested structures enables flexible configuration
hierarchies while maintaining type safety.

The function returns a TypeGuard[CombinatorialObject], allowing static type
checkers to narrow the type of validated objects. This provides both runtime
validation and improved static type safety.

Empty dicts and dataclasses (with no fields) are considered valid and return
True (vacuously true - all zero fields satisfy the iterable requirement).

See Also
--------
combinatorial_config.schemas.CombinatorialObject
    Type alias for validated combinatorial objects (Union[Dict, DataclassProtocol]).
combinatorial_config.schemas.DataclassProtocol
    Structural protocol for dataclass instances.

Examples
--------
Valid combinatorial objects:

>>> from dataclasses import dataclass
>>> from combinatorial_config.validators import is_combinatorial_object
>>>
>>> # Flat configuration with iterable values
>>> config = {
...     "learning_rate": [0.1, 0.01, 0.001],
...     "batch_size": [16, 32, 64],
...     "dropout": [0.1, 0.2, 0.3]
... }
>>> is_combinatorial_object(config)
True
>>>
>>> # Nested configuration (hierarchical structure)
>>> nested_cfg = {
...     "model": {"layers": [2, 4, 8]},
...     "training": {
...         "optimizer": {"lr": [0.1, 0.01]}
...     }
... }
>>> is_combinatorial_object(nested_cfg)
True
>>>
>>> # Empty structures are valid
>>> is_combinatorial_object({})
True

Invalid combinatorial objects:

>>> # Scalar values (not iterable)
>>> scalar_cfg = {"lr": 0.01, "bs": 32}
>>> is_combinatorial_object(scalar_cfg)
False
>>>
>>> # String values (explicitly rejected)
>>> string_cfg = {"name": "experiment"}
>>> is_combinatorial_object(string_cfg)
False

Type narrowing with TypeGuard:

>>> from typing import Any
>>> obj: Any = {"lr": [0.1, 0.01], "bs": [16, 32]}
>>> if is_combinatorial_object(obj):
...     # obj is now narrowed to CombinatorialObject type
...     print(f"Valid config with {len(obj)} fields")
Valid config with 2 fields
"""

from typing import Any, TypeGuard, Tuple
from dataclasses import is_dataclass
from collections.abc import Iterable

from ..schemas import CombinatorialObject


# TODO: optional field에 대한 검증 추가 필요
# nested field 지원: 재귀적으로 combinatorial object 검증


def is_combinatorial_object(
    obj: Any,
    except_fields: Tuple[str, ...] = tuple(),
) -> TypeGuard[CombinatorialObject]:
    """
    Validate whether an object is a valid combinatorial configuration object.

    A valid combinatorial object must satisfy the following conditions:
    1. Be either a dict or a dataclass instance (not a class)
    2. All field values must be either:
       - Iterable (list, tuple, set, range, etc.) - excluding strings
       - Valid combinatorial objects (for nested/hierarchical structures)

    This supports both flat configurations with iterable values and nested
    hierarchical configurations.

    This function serves as a TypeGuard, allowing type checkers to narrow the
    type of the input object to CombinatorialObject when the function returns True.

    Parameters
    ----------
    obj : Any
        The object to validate. Can be of any type.
    except_fields : Tuple[str, ...], optional
        Field names to exclude from validation. These fields will not be
        checked. Default is an empty tuple.

    Returns
    -------
    bool
        True if obj is a dict or dataclass instance with all field values being
        iterable or valid combinatorial objects (except excluded fields); False otherwise.

    Notes
    -----
    String values are explicitly rejected as field values despite being iterable
    in Python, as they represent atomic values rather than collections in the
    context of combinatorial configurations.

    The recursive validation for nested structures allows building hierarchical
    configuration trees where internal nodes are combinatorial objects and leaf
    nodes are iterables containing actual configuration values.

    The function uses structural checking for dataclasses via the
    `__dataclass_fields__` attribute rather than inheritance, making it
    compatible with any dataclass created with the standard @dataclass decorator.

    Examples
    --------
    Valid combinatorial objects:

    >>> from dataclasses import dataclass
    >>>
    >>> # Base case: empty structures
    >>> is_combinatorial_object({})
    True
    >>>
    >>> @dataclass
    ... class EmptyConfig:
    ...     pass
    >>> is_combinatorial_object(EmptyConfig())
    True

    >>> # Nested empty structures
    >>> config_dict = {
    ...     "section_a": {},
    ...     "section_b": {
    ...         "subsection": {}
    ...     }
    ... }
    >>> is_combinatorial_object(config_dict)
    True

    Invalid combinatorial objects:

    >>> # Lists are not combinatorial objects
    >>> config_with_list = {"lr": [0.1, 0.01]}
    >>> is_combinatorial_object(config_with_list)
    False

    >>> # Scalars are not combinatorial objects
    >>> scalar_config = {"lr": 0.1, "bs": 32}
    >>> is_combinatorial_object(scalar_config)
    False

    >>> # Primitives are not dicts or dataclasses
    >>> is_combinatorial_object(42)
    False

    >>> is_combinatorial_object([1, 2, 3])
    False
    """
    # 1. dict 또는 dataclass 인스턴스인지 확인
    # dataclass 클래스 자체는 제외 (인스턴스만 허용)
    if isinstance(obj, dict):
        pass  # dict는 OK
    elif is_dataclass(obj) and not isinstance(obj, type):
        pass  # dataclass 인스턴스는 OK
    else:
        return False

    # 2. 모든 필드 검증
    # except_fields를 제외한 검증 대상 키 목록 추출
    all_keys = obj.keys() if isinstance(obj, dict) else obj.__dataclass_fields__.keys()
    keys = tuple(set(all_keys) - set(except_fields))

    # 각 필드 값에 대한 유효성 검증 (iterable 또는 nested combinatorial object)
    for key in keys:
        value = obj[key] if isinstance(obj, dict) else getattr(obj, key)

        # 조건 1: 문자열은 명시적으로 거부 (iterable이지만 atomic value로 간주)
        if isinstance(value, str):
            return False

        # 조건 2: iterable이거나 combinatorial object여야 함
        # - iterable: list, tuple, set, range 등 조합 생성을 위한 값들
        # - combinatorial object: nested 구조 지원 (재귀)
        is_iterable = isinstance(value, Iterable)
        is_nested_combinatorial = is_combinatorial_object(value)

        if not (is_iterable or is_nested_combinatorial):
            return False

    return True
