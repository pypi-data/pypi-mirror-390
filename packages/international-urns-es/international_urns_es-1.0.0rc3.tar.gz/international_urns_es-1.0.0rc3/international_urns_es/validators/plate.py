"""Spanish vehicle license plate validator.

Spanish license plates have evolved through different formats:
- Current format (since 2000): 4 digits + 3 letters (e.g., 1234ABC)
- Old format (1971-2000): 1-2 province letters + 4 digits + 1-2 letters (e.g., M1234AB)
"""

import re
from typing import ClassVar

from international_urns import URNValidator


class PlateValidator(URNValidator):
    """Validator for Spanish vehicle license plates.

    Supports both current and historical license plate formats:

    Current format (since 2000):
    - 4 digits followed by 3 consonants (excluding vowels and Ñ, Q)
    - Example: 1234BBC

    Old format (1971-2000):
    - 1-2 province letters + 4 digits + 1-2 letters
    - Examples: M1234AB, MA1234B

    Valid formats:
    - urn:es:plate:1234BBC (current)
    - urn:es:plate:M1234AB (old)

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["plate", "matricula"]

    # Current format: 4 digits + 3 consonants (no vowels, Ñ, Q)
    # Allowed consonants: BCDFGHJKLMNPRSTVWXYZ
    _CURRENT_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^(\d{4})([BCDFGHJKLMNPRSTVWXYZ]{3})$"
    )

    # Old format: 1-2 letters + 4 digits + 1-2 letters
    _OLD_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([A-Z]{1,2})(\d{4})([A-Z]{1,2})$")

    # Special formats (diplomatic, official, etc.)
    _SPECIAL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^(CD|CC|E|ET|CMD|DGP|MF|MMA|PMM|CNP)(\d{4,5})$"
    )

    # Valid province codes for old format
    _PROVINCE_CODES: ClassVar[set[str]] = {
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
    }

    def validate(self, urn: str) -> str:
        """Validate a Spanish license plate URN.

        :param urn: The URN to validate
        :type urn: str
        :return: The validated URN
        :rtype: str
        :raises ValueError: If the URN is invalid
        """
        # Parse URN
        parts = urn.split(":")
        if len(parts) != 4:
            raise ValueError(f"Invalid URN format: {urn}")

        scheme, country, doc_type, value = parts

        if scheme.lower() != "urn":
            raise ValueError(f"Invalid URN scheme: {scheme}")

        if country.lower() != self.country_code:
            raise ValueError(f"Invalid country code: {country}")

        if doc_type.lower() not in self.document_types:
            raise ValueError(f"Invalid document type: {doc_type}")

        # Validate plate format
        self._validate_plate(value)

        # Return normalized URN (lowercase scheme, country, and doc_type)
        return f"urn:{country.lower()}:{doc_type.lower()}:{value}"

    def _validate_plate(self, plate: str) -> None:
        """Validate license plate format.

        :param plate: The license plate value to validate
        :type plate: str
        :raises ValueError: If the license plate is invalid
        """
        # Remove spaces and hyphens, convert to uppercase
        plate = plate.replace(" ", "").replace("-", "").upper()

        # Try current format
        if self._CURRENT_PATTERN.match(plate):
            return

        # Try old format
        old_match = self._OLD_PATTERN.match(plate)
        if old_match:
            province = old_match.group(1)
            if province in self._PROVINCE_CODES:
                return
            raise ValueError(f"Invalid province code in old format plate: {province}")

        # Try special formats
        if self._SPECIAL_PATTERN.match(plate):
            return

        raise ValueError(
            f"Invalid license plate format: {plate}. "
            "Expected current format (1234ABC), old format (M1234AB), "
            "or special format (CD1234)"
        )


__all__ = ["PlateValidator"]
