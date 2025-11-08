"""NIF (Número de Identificación Fiscal) validator for Spain.

The NIF is the tax identification number for individuals in Spain.
For individuals, it can be either a DNI or NIE format.
Format: 12345678Z (DNI) or X1234567L (NIE).
"""

import re
from typing import ClassVar

from international_urns import URNValidator


class NIFValidator(URNValidator):
    """Validator for Spanish NIF (Número de Identificación Fiscal) for individuals.

    The NIF for individuals accepts both DNI and NIE formats:
    - DNI format: 8 digits + check letter
    - NIE format: Letter (X, Y, Z) + 7 digits + check letter

    Valid formats:
    - urn:es:nif:12345678Z (DNI format)
    - urn:es:nif:X1234567L (NIE format)

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["nif"]

    # Check letters for NIF validation (same as DNI/NIE)
    _CHECK_LETTERS: ClassVar[str] = "TRWAGMYFPDXBNJZSQVHLCKE"
    _DNI_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^(\d{8})([A-Z])$")
    _NIE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([XYZ])(\d{7})([A-Z])$")

    # Mapping for NIE prefix letters to numbers
    _PREFIX_MAP: ClassVar[dict[str, str]] = {"X": "0", "Y": "1", "Z": "2"}

    def validate(self, urn: str) -> str:
        """Validate a Spanish NIF URN.

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

        # Validate NIF format (DNI or NIE)
        self._validate_nif(value)

        # Return normalized URN (lowercase scheme, country, and doc_type)
        return f"urn:{country.lower()}:{doc_type.lower()}:{value}"

    def _validate_nif(self, nif: str) -> None:
        """Validate NIF number and check letter.

        Accepts both DNI and NIE formats.

        :param nif: The NIF value to validate
        :type nif: str
        :raises ValueError: If the NIF is invalid
        """
        # Convert to uppercase for validation
        nif = nif.upper()

        # Try DNI format first
        dni_match = self._DNI_PATTERN.match(nif)
        if dni_match:
            self._validate_dni_format(dni_match)
            return

        # Try NIE format
        nie_match = self._NIE_PATTERN.match(nif)
        if nie_match:
            self._validate_nie_format(nie_match)
            return

        raise ValueError(
            f"Invalid NIF format: {nif}. "
            "Expected DNI format (8 digits + letter) or NIE format (X/Y/Z + 7 digits + letter)"
        )

    def _validate_dni_format(self, match: re.Match[str]) -> None:
        """Validate DNI format check letter.

        :param match: Regex match object for DNI pattern
        :type match: re.Match[str]
        :raises ValueError: If check letter is invalid
        """
        number_str, letter = match.groups()
        number = int(number_str)
        expected_letter = self._CHECK_LETTERS[number % 23]

        if letter != expected_letter:
            raise ValueError(f"Invalid NIF check letter. Expected {expected_letter}, got {letter}")

    def _validate_nie_format(self, match: re.Match[str]) -> None:
        """Validate NIE format check letter.

        :param match: Regex match object for NIE pattern
        :type match: re.Match[str]
        :raises ValueError: If check letter is invalid
        """
        prefix, number_str, letter = match.groups()
        number = int(self._PREFIX_MAP[prefix] + number_str)
        expected_letter = self._CHECK_LETTERS[number % 23]

        if letter != expected_letter:
            raise ValueError(f"Invalid NIF check letter. Expected {expected_letter}, got {letter}")


__all__ = ["NIFValidator"]
