"""CIF (Código de Identificación Fiscal) validator for Spain.

The CIF is the tax identification code for Spanish companies and organizations.
Format: Letter (organization type) + 7 digits + check digit (letter or number).
Example: A12345674, B1234567X
"""

import re
from typing import ClassVar

from international_urns import URNValidator


class CIFValidator(URNValidator):
    """Validator for Spanish CIF (Código de Identificación Fiscal).

    The CIF consists of:
    - 1 letter indicating organization type (A-W, except I, O, U)
    - 7 digits
    - 1 check character (letter or digit depending on organization type)

    Valid format: urn:es:cif:A12345674 or urn:es:cif:B1234567X

    Organization type letters:
    - A: Sociedades Anónimas
    - B: Sociedades de Responsabilidad Limitada
    - C: Sociedades Colectivas
    - D: Sociedades Comanditarias
    - E: Comunidades de Bienes
    - F: Sociedades Cooperativas
    - G: Asociaciones
    - H: Comunidades de Propietarios
    - J: Sociedades Civiles
    - N: Entidades Extranjeras
    - P: Corporaciones Locales
    - Q: Organismos Autónomos
    - R: Congregaciones e Instituciones Religiosas
    - S: Órganos de la Administración del Estado
    - U: Uniones Temporales de Empresas
    - V: Otros tipos no definidos
    - W: Establecimientos permanentes de entidades no residentes

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["cif"]

    _CIF_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([A-HJNPQRSUVW])(\d{7})([A-J0-9])$")

    # Organization types that must have a letter as check digit
    _LETTER_CHECK_TYPES: ClassVar[set[str]] = {"N", "P", "Q", "R", "S", "W"}

    # Organization types that must have a number as check digit
    _NUMBER_CHECK_TYPES: ClassVar[set[str]] = {"A", "B", "E", "H"}

    # Check letters for CIF validation
    _CHECK_LETTERS: ClassVar[str] = "JABCDEFGHI"

    def validate(self, urn: str) -> str:
        """Validate a Spanish CIF URN.

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

        # Validate CIF format and check digit
        self._validate_cif(value)

        # Return normalized URN (lowercase scheme, country, and doc_type)
        return f"urn:{country.lower()}:{doc_type.lower()}:{value}"

    def _validate_cif(self, cif: str) -> None:
        """Validate CIF format and check digit.

        :param cif: The CIF value to validate
        :type cif: str
        :raises ValueError: If the CIF is invalid
        """
        # Convert to uppercase for validation
        cif = cif.upper()

        match = self._CIF_PATTERN.match(cif)
        if not match:
            raise ValueError(
                f"Invalid CIF format: {cif}. Expected letter + 7 digits + check character"
            )

        org_type, digits, check_char = match.groups()

        # Calculate check digit
        expected_check = self._calculate_check_digit(digits, org_type)

        # Validate check character based on organization type
        if org_type in self._LETTER_CHECK_TYPES:
            # Must be a letter
            if not check_char.isalpha():
                raise ValueError(
                    f"Invalid CIF check character: {cif}. "
                    f"Organization type {org_type} requires a letter"
                )
            if check_char != expected_check:
                raise ValueError(
                    f"Invalid CIF check character: {cif}. "
                    f"Expected {expected_check}, got {check_char}"
                )
        elif org_type in self._NUMBER_CHECK_TYPES:
            # Must be a number
            if not check_char.isdigit():
                raise ValueError(
                    f"Invalid CIF check character: {cif}. "
                    f"Organization type {org_type} requires a digit"
                )
            if check_char != expected_check:
                raise ValueError(
                    f"Invalid CIF check character: {cif}. "
                    f"Expected {expected_check}, got {check_char}"
                )
        else:
            # Can be either letter or number, but must match
            if check_char != expected_check:
                # Try the alternative format
                if expected_check.isdigit():
                    alt_check = str((10 - int(expected_check)) % 10)
                else:
                    alt_check = expected_check
                if check_char != alt_check:
                    raise ValueError(
                        f"Invalid CIF check character: {cif}. "
                        f"Expected {expected_check} or {alt_check}, got {check_char}"
                    )

    def _calculate_check_digit(self, digits: str, org_type: str) -> str:
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
        if org_type in self._LETTER_CHECK_TYPES:
            return self._CHECK_LETTERS[check_digit]
        elif org_type in self._NUMBER_CHECK_TYPES:
            return str(check_digit)
        else:
            # For other types, return letter (most common)
            return self._CHECK_LETTERS[check_digit]


__all__ = ["CIFValidator"]
