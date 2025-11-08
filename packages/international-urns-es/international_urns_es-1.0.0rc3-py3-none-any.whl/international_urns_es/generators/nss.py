"""NSS (Número de la Seguridad Social) generator for Spain.

The NSS is the Social Security Number used in Spain.
Format: 12 digits (province + sequential + check digits).
"""

import random

# Valid province codes (01-52) and special codes (66-99)
_VALID_PROVINCES = list(range(1, 53)) + list(range(66, 100))


def generate_nss() -> str:
    """Generate a random valid NSS URN.

    The NSS consists of:
    - 2 digits: Province code (01-52 or 66-99)
    - 8 digits: Sequential number
    - 2 digits: Check digits (calculated using modulo 97)

    :return: A valid NSS URN (e.g., urn:es:nss:281234567840)
    :rtype: str
    """
    # Select random province code
    province = random.choice(_VALID_PROVINCES)

    # Generate 8 random digits for sequential number
    sequential = random.randint(0, 99999999)

    # Combine province and sequential to calculate check digits
    base_number = f"{province:02d}{sequential:08d}"
    base_int = int(base_number)

    # Calculate check digits using modulo 97
    check_digits = base_int % 97

    # Format as URN (without slashes for simplicity)
    return f"urn:es:nss:{base_number}{check_digits:02d}"


__all__ = ["generate_nss"]
