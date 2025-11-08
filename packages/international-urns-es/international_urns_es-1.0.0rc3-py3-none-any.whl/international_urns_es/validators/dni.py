"""DNI (Documento Nacional de Identidad) validator for Spain.

The DNI is the national identity document for Spanish citizens.
Format: 8 digits followed by a check letter (e.g., 12345678Z).
"""

import re
from typing import ClassVar

from international_urns import URNValidator


class DNIValidator(URNValidator):
    """Validator for Spanish DNI (Documento Nacional de Identidad).

    The DNI consists of 8 digits followed by a check letter calculated
    using modulo 23 algorithm.

    Valid format: urn:es:dni:12345678Z

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["dni"]

    # Check letters for DNI validation (modulo 23)
    _CHECK_LETTERS: ClassVar[str] = "TRWAGMYFPDXBNJZSQVHLCKE"
    _DNI_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^(\d{8})([A-Z])$")

    def validate(self, urn: str) -> str:
        """Validate a Spanish DNI URN.

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

        # Validate DNI format and check letter
        self._validate_dni(value)

        # Return normalized URN (lowercase scheme, country, and doc_type)
        return f"urn:{country.lower()}:{doc_type.lower()}:{value}"

    def _validate_dni(self, dni: str) -> None:
        """Validate DNI number and check letter.

        :param dni: The DNI value to validate
        :type dni: str
        :raises ValueError: If the DNI is invalid
        """
        # Convert to uppercase for validation
        dni = dni.upper()

        match = self._DNI_PATTERN.match(dni)
        if not match:
            raise ValueError(f"Invalid DNI format: {dni}. Expected 8 digits followed by a letter")

        number_str, letter = match.groups()
        number = int(number_str)

        # Calculate expected check letter
        expected_letter = self._CHECK_LETTERS[number % 23]

        if letter != expected_letter:
            raise ValueError(
                f"Invalid DNI check letter: {dni}. Expected {expected_letter}, got {letter}"
            )


__all__ = ["DNIValidator"]
