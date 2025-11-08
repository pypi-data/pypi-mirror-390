def is_empty(str_val: str) -> bool:
    return not str_val or not (str_val and str_val.strip())

def safe_str_to_number(value):
    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    raise ValueError(f"'{value}' is not a valid number.")

def to_comma_separated(value) -> str:
    """
    Converts a value to a comma-separated string.

    Args:
        value: can be int, str, list[int], list[str], or None

    Returns:
        String with comma-separated values
    """
    if value is None:
        return ""

    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)

    return str(value)