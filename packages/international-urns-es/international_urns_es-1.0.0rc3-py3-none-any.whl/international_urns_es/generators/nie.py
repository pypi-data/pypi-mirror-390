"""NIE (Número de Identidad de Extranjero) generator for Spain.

The NIE is the identification number for foreign nationals in Spain.
Format: Letter (X, Y, or Z) + 7 digits + check letter (e.g., X1234567L).
"""

import random

# Check letters for NIE validation (same as DNI)
_CHECK_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"

# Valid prefix letters
_PREFIXES = ["X", "Y", "Z"]

# Mapping for prefix letters to numbers for check calculation
_PREFIX_MAP = {"X": "0", "Y": "1", "Z": "2"}


def generate_nie() -> str:
    """Generate a random valid NIE URN.

    :return: A valid NIE URN (e.g., urn:es:nie:X1234567L)
    :rtype: str
    """
    # Select random prefix
    prefix = random.choice(_PREFIXES)

    # Generate 7 random digits
    number = random.randint(0, 9999999)

    # Calculate check letter (using prefix mapping)
    full_number = int(_PREFIX_MAP[prefix] + f"{number:07d}")
    check_letter = _CHECK_LETTERS[full_number % 23]

    # Format as URN
    return f"urn:es:nie:{prefix}{number:07d}{check_letter}"


__all__ = ["generate_nie"]
