"""License Plate (Matrícula) generator for Spain.

Spanish vehicle license plates. Supports current, historical, and special formats.
"""

import random

# Current format: consonants only (no vowels, Ñ, or Q)
_CONSONANTS = [
    "B",
    "C",
    "D",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "R",
    "S",
    "T",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]

# Old format province codes (most common ones)
_PROVINCE_CODES = [
    "A",
    "AB",
    "AL",
    "AV",
    "B",
    "BA",
    "BI",
    "BU",
    "C",
    "CA",
    "CC",
    "CE",
    "CO",
    "CR",
    "CS",
    "CU",
    "GC",
    "GI",
    "GR",
    "GU",
    "H",
    "HU",
    "J",
    "L",
    "LE",
    "LO",
    "LU",
    "M",
    "MA",
    "ML",
    "MU",
    "NA",
    "O",
    "OR",
    "P",
    "PM",
    "PO",
    "S",
    "SA",
    "SE",
    "SG",
    "SO",
    "SS",
    "T",
    "TE",
    "TF",
    "TO",
    "V",
    "VA",
    "VI",
    "Z",
    "ZA",
]

# Special format prefixes
_SPECIAL_PREFIXES = ["CD", "CC", "E", "ET", "CMD", "DGP", "MF", "MMA", "PMM", "CNP"]

# All letters for old format ending
_ALL_LETTERS = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]


def _generate_current_format() -> str:
    """Generate a current format plate (4 digits + 3 consonants).

    :return: A plate in current format (e.g., 1234BBC)
    :rtype: str
    """
    digits = f"{random.randint(0, 9999):04d}"
    consonants = "".join(random.choice(_CONSONANTS) for _ in range(3))
    return f"{digits}{consonants}"


def _generate_old_format() -> str:
    """Generate an old format plate (province + 4 digits + 1-2 letters).

    :return: A plate in old format (e.g., M1234AB)
    :rtype: str
    """
    province = random.choice(_PROVINCE_CODES)
    digits = f"{random.randint(0, 9999):04d}"
    # 1 or 2 letters at the end
    num_letters = random.choice([1, 2])
    letters = "".join(random.choice(_ALL_LETTERS) for _ in range(num_letters))
    return f"{province}{digits}{letters}"


def _generate_special_format() -> str:
    """Generate a special format plate (prefix + 4-5 digits).

    :return: A plate in special format (e.g., CD1234)
    :rtype: str
    """
    prefix = random.choice(_SPECIAL_PREFIXES)
    # Most special plates have 4 or 5 digits
    num_digits = random.choice([4, 5])
    if num_digits == 4:
        digits = f"{random.randint(0, 9999):04d}"
    else:
        digits = f"{random.randint(0, 99999):05d}"
    return f"{prefix}{digits}"


def generate_plate() -> str:
    """Generate a random valid Spanish license plate URN.

    This generator randomly selects between current, old, and special formats
    with weighted probabilities (70% current, 20% old, 10% special).

    :return: A valid plate URN (e.g., urn:es:plate:1234BBC)
    :rtype: str
    """
    # Weighted random selection of format
    format_choice = random.choices(["current", "old", "special"], weights=[0.7, 0.2, 0.1], k=1)[0]

    if format_choice == "current":
        plate = _generate_current_format()
    elif format_choice == "old":
        plate = _generate_old_format()
    else:
        plate = _generate_special_format()

    # Format as URN
    return f"urn:es:plate:{plate}"


__all__ = ["generate_plate"]
