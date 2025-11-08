"""NIE (Número de Identidad de Extranjero) validator for Spain.

The NIE is the identification number for foreign nationals in Spain.
Format: Letter (X, Y, or Z) + 7 digits + check letter (e.g., X1234567L).
"""

import re
from typing import ClassVar

from international_urns import URNValidator


class NIEValidator(URNValidator):
    """Validator for Spanish NIE (Número de Identidad de Extranjero).

    The NIE consists of a prefix letter (X, Y, or Z), 7 digits, and a check letter
    calculated using the same algorithm as DNI.

    Valid format: urn:es:nie:X1234567L

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["nie"]

    # Check letters for NIE validation (same as DNI)
    _CHECK_LETTERS: ClassVar[str] = "TRWAGMYFPDXBNJZSQVHLCKE"
    _NIE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([XYZ])(\d{7})([A-Z])$")

    # Mapping for prefix letters to numbers for check calculation
    _PREFIX_MAP: ClassVar[dict[str, str]] = {"X": "0", "Y": "1", "Z": "2"}

    def validate(self, urn: str) -> str:
        """Validate a Spanish NIE URN.

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

        # Validate NIE format and check letter
        self._validate_nie(value)

        # Return normalized URN (lowercase scheme, country, and doc_type)
        return f"urn:{country.lower()}:{doc_type.lower()}:{value}"

    def _validate_nie(self, nie: str) -> None:
        """Validate NIE number and check letter.

        :param nie: The NIE value to validate
        :type nie: str
        :raises ValueError: If the NIE is invalid
        """
        # Convert to uppercase for validation
        nie = nie.upper()

        match = self._NIE_PATTERN.match(nie)
        if not match:
            raise ValueError(
                f"Invalid NIE format: {nie}. Expected letter (X, Y, or Z) + 7 digits + check letter"
            )

        prefix, number_str, letter = match.groups()

        # Replace prefix letter with corresponding digit
        number = int(self._PREFIX_MAP[prefix] + number_str)

        # Calculate expected check letter
        expected_letter = self._CHECK_LETTERS[number % 23]

        if letter != expected_letter:
            raise ValueError(
                f"Invalid NIE check letter: {nie}. Expected {expected_letter}, got {letter}"
            )


__all__ = ["NIEValidator"]
