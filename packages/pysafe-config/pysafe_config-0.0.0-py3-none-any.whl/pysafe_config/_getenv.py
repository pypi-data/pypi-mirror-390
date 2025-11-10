import os
from typing import TypeVar, Callable

T = TypeVar("T")

_allowed_types = [bool, int, float, str]


def _getenv(
    var_name: str,
    return_type: type[T],
    helper_function: Callable[[str], T],
    default: T | None = None,
    required: bool = False,
) -> T | None:
    """
    The function gets the value of an environment variable specified by `var_name` and
    coerces the object into `return_type` via the use of a helper function.

    If the environment variable is not set:
      - If `required` is True, a RuntimeError is raised indicating that the variable
        is mandatory.
      - If `required` is False, the function returns the default value, which may be
        None if no default is provided.

    Args:
        var_name (str): The name of the environment variable to retrieve.
        default (type[T] | None, optional): The value to return if the environment variable
            is not set and required is False. Defaults to None.
        required (bool, optional): Whether the environment variable is mandatory. If True
            and the variable is not set, a RuntimeError is raised. Defaults to False.

    Returns:
        T | None: The value of the environment variable coerced into a `return_type` type, or
                  `default` if the variable is missing and not required.

    Raises:
        TypeError: If the environment variable is set but cannot be converted to a string.
        RuntimeError: If the environment variable is required but not set.
        TypeError: If `return_type` is not in the `allowed_types` set.
                   This may be updated in a future version to include Enums.
    """
    value: str | None = os.getenv(var_name)

    if value is None and required is True:
        raise RuntimeError(f"Missing required environment variable '{var_name}'.")

    elif value is not None and return_type not in _allowed_types:
        raise TypeError(
            f"return_type '{return_type}' "
            f"must be on of [{', '.join([item.__name__ for item in _allowed_types])}]"
        )

    elif value is not None:
        try:
            return helper_function(value)
        except ValueError as e:
            raise ValueError(
                f"Value of environment variable '{var_name}' cannot be converted to {return_type.__name__} '{value}'."
            ) from e
    else:
        return default


def _getenv_strict(
    var_name: str, return_type: type[T], helper_function: Callable[[str], T]
) -> T:
    """
    Stricter version of _getenv for when the user requires that the environment variable
    cannot be None, reducing boilerplate code for None checks and conforming with mypy.

    The function gets the value of an environment variable specified by `var_name` and
    coerces the object into `return_type` via the use of a helper function.

    An exception is raised if the environment variable is not set or the object cannot
    be converted to `return_type`

    Args:
        var_name (str): The name of the environment variable to retrieve.

    Returns:
        str: The string value of the environment variable.

    Raises:
        TypeError: If the environment variable is set but cannot be converted to a string.
        RuntimeError: If the environment variable is not set.
        TypeError: If `return_type` is not in the `allowed_types` set.
                   This may be updated in a future version to include Enums.
    """
    value = os.getenv(var_name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable '{var_name}'.")

    if return_type not in _allowed_types:
        raise TypeError(
            f"return_type '{return_type}' "
            f"must be on of [{', '.join([item.__name__ for item in _allowed_types])}]"
        )

    try:
        result = helper_function(value)
    except ValueError as e:
        raise ValueError(
            f"Value of environment variable '{var_name}' cannot be converted to "
            f"{return_type.__name__}: '{value}'"
        ) from e

    # Here we help MyPy understand the narrowing
    if not isinstance(result, return_type):
        raise TypeError(
            f"Converter for {return_type} returned unexpected type: {type(result)}"
        )

    return result
