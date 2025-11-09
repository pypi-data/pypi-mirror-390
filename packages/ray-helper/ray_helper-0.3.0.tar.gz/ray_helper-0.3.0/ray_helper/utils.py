def to_uppercase(text: str) -> str:
    """
    Converts a string to uppercase.
    :param text: The input string.
    :return: Uppercase version of the string.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    return text.upper()
def to_lowercase(text: str) -> str:
    """
    Converts a string to lowercase.
    :param text: The input string.
    :return: Lowercase version of the string.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    return text.lower()
def swap_case(text: str) -> str:
    """
    Converts uppercase letters to lowercase and lowercase letters to uppercase.
    :param text: The input string.
    :return: String with swapped case.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    return text.swapcase()