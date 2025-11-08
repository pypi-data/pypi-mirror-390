"""DIR3 (Directorio Común de unidades y oficinas) validator for Spain.

DIR3 is the Common Directory of units and offices of the Spanish Public Administration.
Format: 9 character alphanumeric code.
Examples: E00010201, A01000001, L01000001, GE0000001, O00000001
"""

import re
from typing import ClassVar

from international_urns import URNValidator


class DIR3Validator(URNValidator):
    """Validator for Spanish DIR3 codes.

    DIR3 codes identify administrative units and offices in the Spanish
    Public Administration. They consist of exactly 9 alphanumeric characters.

    Valid format: urn:es:dir3:E00010201

    The code structure:
    - First 1-2 characters: Administration level identifier
      E=State, A=Autonomous, L=Local, U=Universities, I=Institutions,
      J=Justice, O=Offices, GE=Economic Units, EC=Collaborating Entities
    - Remaining 7-8 digits: Identifier (structure varies by type)

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["dir3"]

    # DIR3 pattern: 1-2 letter prefix + remaining digits to total 9 chars
    _DIR3_PATTERN_SINGLE: ClassVar[re.Pattern[str]] = re.compile(r"^([EALUIJO])(\d{8})$")
    _DIR3_PATTERN_DOUBLE: ClassVar[re.Pattern[str]] = re.compile(r"^(GE|EC|EA)(\d{7})$")

    def validate(self, urn: str) -> str:
        """Validate a Spanish DIR3 URN.

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

        # Validate DIR3 format
        self._validate_dir3(value)

        # Return normalized URN (lowercase scheme, country, and doc_type)
        return f"urn:{country.lower()}:{doc_type.lower()}:{value}"

    def _validate_dir3(self, dir3: str) -> None:
        """Validate DIR3 code format.

        :param dir3: The DIR3 value to validate
        :type dir3: str
        :raises ValueError: If the DIR3 code is invalid
        """
        # Convert to uppercase for validation
        dir3 = dir3.upper()

        # Check length (must be exactly 9)
        if len(dir3) != 9:
            raise ValueError(f"Invalid DIR3 length: {dir3}. Expected exactly 9 characters")

        # Try single letter prefix pattern first
        match_single = self._DIR3_PATTERN_SINGLE.match(dir3)
        if match_single:
            return

        # Try double letter prefix pattern
        match_double = self._DIR3_PATTERN_DOUBLE.match(dir3)
        if match_double:
            return

        # If neither pattern matches, provide detailed error
        raise ValueError(
            f"Invalid DIR3 format: {dir3}. Expected format: "
            "E/A/L/U/I/J/O + 8 digits, or GE/EC/EA + 7 digits"
        )


__all__ = ["DIR3Validator"]
