# combinatorial-config

A Python library for automatically generating all combinations of experiment configurations.

## Background

This library was born out of a need while using Hydra for experiment configuration management. We wanted an easy way to generate all combinations of multiple hyperparameters. This library automatically generates combinations of experiment variables, enabling systematic exploration of all possible experiment configurations.

## Installation

### For Developers

If you're contributing to the project or need the latest features, install from source:

```bash
# Clone the repository
git clone https://github.com/your-org/combinatorial-config.git
cd combinatorial-config

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Or using rye
rye sync
```

### For Researchers and End Users

Install the stable release from PyPI:

```bash
pip install combinatorial-config
```

Or using rye:

```bash
rye add combinatorial-config
```

**Requirements:**
- Python 3.8+

## Main Feature: `generate_combinations`

The `generate_combinations` function takes a combinatorial configuration object (dict or dataclass) and generates all possible combinations.

### Basic Usage

```python
from combinatorial_config import generate_combinations

# Dictionary-based configuration
config = {
    "learning_rate": [0.1, 0.01],
    "batch_size": [16, 32]
}

combinations = list(generate_combinations(config))
# Result: 4 combinations
# [
#     {'learning_rate': 0.1, 'batch_size': 16},
#     {'learning_rate': 0.1, 'batch_size': 32},
#     {'learning_rate': 0.01, 'batch_size': 16},
#     {'learning_rate': 0.01, 'batch_size': 32}
# ]
```

### Nested Structure Support

Nested configuration structures are processed recursively:

```python
config = {
    "model": {
        "layers": [2, 4],
        "activation": ["relu", "tanh"]
    },
    "training": {
        "epochs": [10, 20],
        "optimizer": ["adam"]
    }
}

combinations = list(generate_combinations(config))
# model: 2×2=4 combinations, training: 2×1=2 combinations
# Total: 4×2=8 combinations generated
```

### Range Field Support

You can use tuples to express ranges concisely:

```python
config = {
    "epochs": (0, 3),  # Automatically converted to [0, 1, 2]
    "optimizer": ["adam", "sgd"]
}

combinations = list(generate_combinations(config))
# 3 epochs × 2 optimizers = 6 combinations
```

## Type-Safe Dataclass Usage

When using dataclasses, to operate in a type-safe manner, you must **explicitly define both the original dataclass and a dataclass with all fields converted to lists**.

### Why Do We Need Two Dataclasses?

Python's type system has limitations in handling dynamic types at runtime. The `generate_combinations` function:

1. **Input**: A combinatorial configuration dataclass where all fields are `list` types
2. **Output**: A realized combination dict where each field is a single value

To accurately distinguish between these two types, explicit type definitions are necessary.

### Example

```python
from dataclasses import dataclass
from combinatorial_config import generate_combinations
from typing import Iterator

# Original configuration type: all fields are lists
@dataclass
class ExperimentConfig:
    learning_rate: list[float]
    batch_size: list[int]
    optimizer: list[str]

# Realized combination type: all fields are single values
@dataclass
class RealizedConfig:
    learning_rate: float
    batch_size: int
    optimizer: str

# Type-safe usage
def run_experiments(config: ExperimentConfig) -> Iterator[RealizedConfig]:
    for combo_dict in generate_combinations(config):
        # combo_dict is a dict, so convert to RealizedConfig
        realized = RealizedConfig(**combo_dict)
        yield realized

# Usage example
config = ExperimentConfig(
    learning_rate=[0.1, 0.01],
    batch_size=[16, 32],
    optimizer=["adam", "sgd"]
)

for realized in run_experiments(config):
    print(f"LR: {realized.learning_rate}, Batch: {realized.batch_size}, Opt: {realized.optimizer}")
```

### Limitations of Type Checkers

Python's type checkers (mypy, pyright, etc.) can only know that `generate_combinations` returns a `dict`. They cannot infer the specific types of each field (e.g., `learning_rate: float`). Therefore, to ensure type safety:

1. **Input type**: `ExperimentConfig` (all fields are `list`)
2. **Output type**: `RealizedConfig` (all fields are single values)

You must explicitly define these two types and convert the result of `generate_combinations` to the appropriate type.

### Nested Structures

The same principle applies to nested structures:

```python
@dataclass
class ModelConfig:
    layers: list[int]
    activation: list[str]

@dataclass
class TrainingConfig:
    epochs: list[int]
    optimizer: list[str]

# Combinatorial configuration
@dataclass
class ExperimentConfig:
    model: ModelConfig
    training: TrainingConfig

# Realized combinations
@dataclass
class RealizedModelConfig:
    layers: int
    activation: str

@dataclass
class RealizedTrainingConfig:
    epochs: int
    optimizer: str

@dataclass
class RealizedConfig:
    model: RealizedModelConfig
    training: RealizedTrainingConfig

# Usage
config = ExperimentConfig(
    model=ModelConfig(layers=[2, 4], activation=["relu", "tanh"]),
    training=TrainingConfig(epochs=[10, 20], optimizer=["adam"])
)

for combo_dict in generate_combinations(config):
    realized = RealizedConfig(
        model=RealizedModelConfig(**combo_dict["model"]),
        training=RealizedTrainingConfig(**combo_dict["training"])
    )
    # Can be used type-safely
    print(realized.model.layers)  # Inferred as int type
```

## Advanced Features

### Field Exclusion

You can exclude specific fields from combination generation:

```python
config = {
    "learning_rate": [0.1, 0.01],
    "batch_size": [16, 32],
    "debug_mode": True  # Excluded from combination generation
}

combinations = list(generate_combinations(config, except_fields=("debug_mode",)))
```

### Undefined Value Alias

The `undefined_value_alias` parameter allows you to use custom placeholder values (like strings) in your configuration files (YAML, JSON, etc.) that will be automatically converted to the `Undefined` sentinel value. This is particularly useful when:

- Working with configuration files where you want to explicitly mark optional fields
- Using string placeholders that are more readable than `None` in YAML/JSON
- Ensuring consistent handling of "missing" or "unspecified" values across your codebase

The conversion works recursively for nested structures, so you can use the alias at any level of nesting.

**Basic Usage:**

```python
from combinatorial_config.schemas import Undefined

config = {
    "optimizer": ["adam", "__undefined__"],
    "epochs": [10, 20]
}

combinations = list(generate_combinations(config, undefined_value_alias="__undefined__"))
# Result: 4 combinations
# [
#     {'optimizer': 'adam', 'epochs': 10},
#     {'optimizer': Undefined, 'epochs': 10},  # "__undefined__" converted to Undefined
#     {'optimizer': 'adam', 'epochs': 20},
#     {'optimizer': Undefined, 'epochs': 20}
# ]

# Check that alias was converted
assert combinations[1]["optimizer"] is Undefined
```

**Nested Structures:**

The alias conversion also works in nested configurations:

```python
config = {
    "model": {
        "type": ["resnet", "__undefined__"],
        "layers": [2, 4]
    },
    "epochs": [10, 20]
}

combinations = list(generate_combinations(config, undefined_value_alias="__undefined__"))
# The "__undefined__" in nested "model.type" is also converted to Undefined
assert combinations[1]["model"]["type"] is Undefined
```

**Use Case: Optional Fields in YAML Configs**

This feature is especially useful when loading configurations from YAML files:

```yaml
# config.yaml
model:
  type: ["resnet", "__undefined__"]  # Some experiments don't specify model type
  layers: [2, 4]
training:
  optimizer: ["adam", "sgd"]
```

```python
import yaml
from combinatorial_config import generate_combinations

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# All "__undefined__" values are converted to Undefined sentinel
for combo in generate_combinations(config, undefined_value_alias="__undefined__"):
    if combo["model"]["type"] is Undefined:
        # Handle case where model type is not specified
        pass
```

## License

MIT License
