import re

# Example allowable
_int_pattern = re.compile(r"^[+-]?\d+$")


def _str_to_int(value: str) -> int:
    """
    Converts a string value to an integer by checking value against a regex.

    This package is strict on what can be parsed from an integer string.

    Valid integer strings must not:
        - Have any whitespace
        - Contain any non-numeric characters other than a
          plus or minus sign at the beginning of the number

    Some valid examples of integer strings are
        - "100"
        - "1"
        - "-50"
        - "+1000"

    Args:
        value (str): The string value to convert.

    Returns:
        int: The integer representation of the string.

    Raises:
        ValueError: If the string cannot be converted to an integer
    """
    if _int_pattern.match(value.strip()):
        return int(value)
    else:
        raise ValueError(f"Value must be valid integer '{value}'")
