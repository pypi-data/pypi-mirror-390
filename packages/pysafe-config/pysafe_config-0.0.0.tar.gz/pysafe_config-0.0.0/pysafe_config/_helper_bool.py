_true_values: set[str] = {
    "true",
    "1",
    "yes",
    "y",
    "on",
    "enable",
    "enabled",
    "t",
}

_false_values: set[str] = {
    "false",
    "0",
    "no",
    "n",
    "off",
    "disable",
    "disabled",
    "f",
}


def _str_to_bool(value: str) -> bool:
    """
    Converts a string value to a boolean.

    Checks if the input string (case-insensitive) is present in a set of
    true or false values. If it matches a true value, it returns
    True. If it matches a false value, it returns False.

    Args:
        value (str): The string value to convert.

    Returns:
        bool: The boolean representation of the string.

    Raises:
        ValueError: If the string cannot be converted to a boolean (i.e., it's not
                    in the true or false value sets).
    """
    value = value.lower()
    if value in _true_values:
        return True
    if value in _false_values:
        return False

    raise ValueError(f"Expected {', '.join(_true_values | _false_values)}")
