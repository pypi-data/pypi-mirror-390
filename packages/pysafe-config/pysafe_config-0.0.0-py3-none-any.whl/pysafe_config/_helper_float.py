import re

_float_pattern = re.compile(r"^[+-]?\d+\.\d+$")


def _str_to_float(value: str) -> float:
    """
    Converts a string value to a float by checking value against a regex.

    Args:
        value (str): The string value to convert.

    Returns:
        bool: The float representation of the string.

    Raises:
        ValueError: If the string cannot be converted to a float
    """
    if _float_pattern.match(value.strip()):
        return float(value)
    else:
        raise ValueError(f"Value must be in format 'x.y' '{value}'")
