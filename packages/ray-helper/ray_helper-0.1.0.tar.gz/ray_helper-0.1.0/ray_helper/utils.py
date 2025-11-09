def to_uppercase(text: str) -> str:
    """
    Converts a string to uppercase.
    :param text: The input string.
    :return: Uppercase version of the string.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    return text.upper()
