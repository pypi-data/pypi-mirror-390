"""DIR3 (Directorio Común) generator for Spain.

DIR3 codes identify administrative units and offices in the Spanish Public Administration.
Format: Exactly 9 characters - either 1 letter + 8 digits or 2 letters + 7 digits.
"""

import random

# Valid single-letter administration level codes (+ 8 digits)
_SINGLE_LETTER_PREFIXES = ["E", "A", "L", "U", "I", "J", "O"]

# Valid double-letter administration level codes (+ 7 digits)
_DOUBLE_LETTER_PREFIXES = ["GE", "EC", "EA"]


def generate_dir3() -> str:
    """Generate a random valid DIR3 URN.

    DIR3 codes are exactly 9 characters total:
    - Single-letter prefix (E, A, L, U, I, J, O) + 8 digits
    - Double-letter prefix (GE, EC, EA) + 7 digits

    :return: A valid DIR3 URN (e.g., urn:es:dir3:E00010201 or urn:es:dir3:GE0001234)
    :rtype: str
    """
    # Randomly choose between single-letter and double-letter prefix (80% single, 20% double)
    if random.random() < 0.8:
        # Single-letter prefix + 8 digits
        prefix = random.choice(_SINGLE_LETTER_PREFIXES)
        digits = f"{random.randint(0, 99999999):08d}"
    else:
        # Double-letter prefix + 7 digits
        prefix = random.choice(_DOUBLE_LETTER_PREFIXES)
        digits = f"{random.randint(0, 9999999):07d}"

    code = f"{prefix}{digits}"

    # Format as URN
    return f"urn:es:dir3:{code}"


__all__ = ["generate_dir3"]
