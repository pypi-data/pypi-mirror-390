"""CIF (Código de Identificación Fiscal) generator for Spain.

The CIF is the tax identification code for Spanish companies and organizations.
Format: Letter (organization type) + 7 digits + check digit (letter or number).
"""

import random

# Valid organization type letters
_ORG_TYPES = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "N", "P", "Q", "R", "S", "U", "V", "W"]

# Organization types that must have a letter as check digit
_LETTER_CHECK_TYPES = {"N", "P", "Q", "R", "S", "W"}

# Organization types that must have a number as check digit
_NUMBER_CHECK_TYPES = {"A", "B", "E", "H"}

# Check letters for CIF validation
_CHECK_LETTERS = "JABCDEFGHI"


def _calculate_check_digit(digits: str, org_type: str) -> str:
    """Calculate CIF check digit.

    :param digits: The 7-digit number part of the CIF
    :type digits: str
    :param org_type: The organization type letter
    :type org_type: str
    :return: The check digit (letter or number as string)
    :rtype: str
    """
    # Sum of digits in even positions (2nd, 4th, 6th)
    even_sum = sum(int(digits[i]) for i in range(1, 7, 2))

    # For odd positions (1st, 3rd, 5th, 7th), double and sum digits
    odd_sum = 0
    for i in range(0, 7, 2):
        doubled = int(digits[i]) * 2
        odd_sum += doubled // 10 + doubled % 10

    # Total sum
    total = even_sum + odd_sum

    # Check digit
    check_digit = (10 - (total % 10)) % 10

    # Return as letter or number based on organization type
    if org_type in _LETTER_CHECK_TYPES:
        return _CHECK_LETTERS[check_digit]
    elif org_type in _NUMBER_CHECK_TYPES:
        return str(check_digit)
    else:
        # For other types, return letter (most common)
        return _CHECK_LETTERS[check_digit]


def generate_cif() -> str:
    """Generate a random valid CIF URN.

    :return: A valid CIF URN (e.g., urn:es:cif:A12345674 or urn:es:cif:N1234567J)
    :rtype: str
    """
    # Select random organization type
    org_type = random.choice(_ORG_TYPES)

    # Generate 7 random digits
    digits = f"{random.randint(0, 9999999):07d}"

    # Calculate check digit
    check_digit = _calculate_check_digit(digits, org_type)

    # Format as URN
    return f"urn:es:cif:{org_type}{digits}{check_digit}"


__all__ = ["generate_cif"]
