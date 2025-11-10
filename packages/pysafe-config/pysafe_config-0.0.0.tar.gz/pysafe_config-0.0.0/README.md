# pysafe-config

`pysafe-config` is a lightweight Python package designed to simplify and secure the process of reading environment variables. It provides a set of functions for each of the common types used for environment variables to reduce boilerplate code, enforce type safety, and handle missing variables gracefully, making application config more robust and easier to manage.

## The Problem: Boilerplate and Error-Prone Environment Variable Handling

Without `pysafe-config`, handling environment variables often involves repetitive and error-prone code, especially when dealing with type conversions and mandatory checks. Consider the common scenario of retrieving a `SAMPLING_RATIO` as a float:

```python
import os
SAMPLING_RATIO = os.getenv("SAMPLING_RATIO", None)

if SAMPLING_RATIO is None:
    raise RuntimeError("SAMPLING_RATIO is unset")
else:
    SAMPLING_RATIO = float(SAMPLING_RATIO)
```

This approach is verbose, susceptible to `ValueError` if the conversion fails, and requires explicit checks for `None`.

## The Solution: `pysafe-config`

`pysafe-config` streamlines this process, allowing you to retrieve and validate environment variables with minimal code. The previous example can be reduced to a single, clear line:

```python
from pysafe_config import getenv_float_strict

SAMPLING_RATIO: float = getenv_float_strict("SAMPLING_RATIO")
```

## Features and Benefits

*   **Reduced Boilerplate**: Significantly cuts down the amount of code needed to read and validate environment variables.
*   **Type Safety**: Automatically converts environment variable strings to the desired Python types (bool, int, float, str) and raises `TypeError` if conversion fails. If using the strict version of a getenv function, the return type is guaranteed and will allow mypy to recognise the variable as the correct type.
*   **Strict Mode**: Functions like `getenv_float_strict` ensure that a `RuntimeError` is raised if a mandatory environment variable is not set, preventing silent failures.
*   **Flexible Handling**: Provides both strict and non-strict versions of functions. Non-strict versions (`getenv_bool`, `getenv_float`, etc.) allow you to specify a `default` value and control whether a variable is `required`.
*   **Clear Error Messages**: Provides descriptive error messages for missing or invalid environment variables, aiding in quicker debugging.
*   **Consistent Validation**: Enforces strict validation rules for different types (e.g., specific formats for floats and integers, a predefined set of true/false strings for booleans).

## Installation

#### poetry
```bash
poetry add pysafe-config
```

#### pip
```bash
pip install pysafe-config
```

## Usage

### Getting Started

Import the required function from `pysafe_config`. Public functions can be imported like so:

```python
from pysafe_config import (
    getenv_bool,
    getenv_float,
    getenv_int,
    getenv_str,
    getenv_bool_strict,
    getenv_float_strict,
    getenv_int_strict,
    getenv_str_strict,
)
```

### Strict Retrieval (Recommended for Mandatory Variables)

Use the `_strict` functions when an environment variable *must* be present and correctly typed. These functions will raise a `RuntimeError` if the variable is missing or a `ValueError` if the type conversion fails.

```python
# Mandatory float environment variable
DATABASE_TIMEOUT: float = getenv_float_strict("DATABASE_TIMEOUT")

# Mandatory boolean environment variable
FEATURE_FLAG_ENABLED: bool = getenv_bool_strict("FEATURE_FLAG_ENABLED")

# Mandatory integer environment variable
WORKER_COUNT: int = getenv_int_strict("WORKER_COUNT")

# Mandatory string environment variable
API_KEY: str = getenv_str_strict("API_KEY")
```

### Flexible Retrieval (with Defaults and Optionality)

Use the non-strict functions when an environment variable is optional or has a sensible default value. You can specify `required=False` and provide a `default` value if the variable cannot be found in the environment.

```python
# Optional string with a default value
LOG_LEVEL: str | None = getenv_str("LOG_LEVEL", default="INFO")

# Optional integer, defaults to None if not set
MAX_RETRIES: int | None = getenv_int("MAX_RETRIES")

# Required boolean with no default (will raise RuntimeError if variable is unset in environment)
DEBUG_MODE: bool | None = getenv_bool("DEBUG_MODE", required=True)

# Required boolean with default value specified (will raise RuntimeError if variable is unset in environment)
RETURN_UPSTREAM_ERRORS: bool | None = getenv_bool("DEBUG_MODE", default=True, required=True)
```

### Supported Boolean Values

`pysafe-config` provides robust parsing for boolean environment variables. The following case-insensitive values are recognised:

| True values | False values |
|-------------|--------------|
| "true"      | "false"      |
| "1"         | "0"          |
| "yes"       | "no"         |
| "y"         | "n"          |
| "on"        | "off"        |
| "enable"    | "disable"    |
| "enabled"   | "disabled"   |
| "t"         | "f"          |

### Supported Float Values

Float values must adhere to a strict format:

*   Contain only digits (`0-9`), optionally preceded by a single `+` or `-` sign.
*   Include exactly one decimal point to separate the whole and fractional parts.
*   Not contain any whitespace, commas, or alphabetic characters.

| Valid strings | Invalid strings |
|---------------|-----------------|
| "50.2"        | "50"            |
| "-0.0"        | "5.5.5"         |
| "+1000.5"     | " 12.3"         |
| "-99.0"       | "12,3"          |
| "0.0001"      | "ten"           |
| "+.5"         | "5."            |
| "-1.23"       | "" (empty)      |

### Supported Integer Values

Integer values must adhere to a strict format:

*   Contain only digits (`0-9`), optionally preceded by a single `+` or `-` sign.
*   Not contain any whitespace.
*   Not include decimal points, letters, or special symbols.

| Valid strings | Invalid strings |
|---------------|-----------------|
| "100"         | " 100"          |
| "1"           | "10.5"          |
| "-50"         | "1,000"         |
| "+1000"       | "12a"           |
| "0"           | "++5"           |
| "-0"          | "5-"            |
| "123456"      | "ten"           |
| "-123456"     | "" (empty)      |

## Contributing

Contributions are welcome! Please refer to the `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License.

## Release docs

TODO: add steps on how to release here
