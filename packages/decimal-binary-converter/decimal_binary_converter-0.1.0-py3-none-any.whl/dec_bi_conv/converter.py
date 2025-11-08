"""
decimal_binary_converter.converter
---------------------------------

A module for converting between decimal and binary numbers.
"""

def decimal_to_binary(decimal: int) -> str:
    """
    Converts a decimal integer to its binary representation as a string (no '0b' prefix).

    Args:
        decimal (int): The decimal integer to convert.

    Returns:
        str: Binary representation as a string.

    Raises:
        ValueError: If decimal is not an integer >= 0.

    Example:
        decimal_to_binary(10)
        '1010'
    """
    if not isinstance(decimal, int) or decimal < 0:
        raise ValueError("Input must be a non-negative integer.")
    return bin(decimal)[2:]

def binary_to_decimal(binary: str) -> int:
    """
    Converts a binary string to its decimal integer equivalent.

    Args:
        binary (str): The binary string to convert.

    Returns:
        int: Decimal equivalent of the input binary string.

    Raises:
        ValueError: If binary is not a valid string of 0s and 1s.

    Example:
        binary_to_decimal('1010')
        10
    """
    if not isinstance(binary, str) or any(c not in '01' for c in binary):
        raise ValueError("Input must be a string of 0s and 1s.")
    return int(binary, 2)

