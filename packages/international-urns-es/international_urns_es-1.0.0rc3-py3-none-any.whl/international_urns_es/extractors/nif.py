"""NIF (Número de Identificación Fiscal) extractor for Spain.

Extracts metadata from NIF URNs.
"""

import re
from typing import Any, ClassVar

from international_urns import URNExtractor


class NIFExtractor(URNExtractor):
    """Extractor for Spanish NIF (Número de Identificación Fiscal).

    Extracts the following metadata from NIF URNs:
    - format_type: Either 'dni' or 'nie'
    - number: The numeric portion (8 digits for DNI, 7 for NIE)
    - check_letter: The check letter
    - prefix: The prefix letter (only for NIE format)
    - generation: Description of NIE prefix with historical context (only for NIE format)
    - document_purpose: Purpose of the document
    - is_valid_format: Whether the format is valid

    Base fields (automatically included):
    - country_code: 'es'
    - document_type: 'nif'
    - document_value: The full NIF value

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["nif"]

    _DNI_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^(\d{8})([A-Z])$", re.IGNORECASE)
    _NIE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([XYZ])(\d{7})([A-Z])$", re.IGNORECASE)

    # Generation mappings for NIE prefix letters with historical context
    _PREFIX_DESCRIPTIONS: ClassVar[dict[str, str]] = {
        "X": (
            "Original NIE series, issued until July 15, 2008 (X = 0 for check letter calculation)"
        ),
        "Y": (
            "Second NIE series, issued from July 16, 2008 per Orden INT/2058/2008 "
            "(Y = 1 for check letter calculation)"
        ),
        "Z": "Third NIE series, added to prevent overflow (Z = 2 for check letter calculation)",
    }

    def _extract_metadata(
        self,
        country_code: str,
        document_type: str,
        document_value: str,
        nss_parts: list[str],
    ) -> dict[str, Any]:
        """Extract NIF-specific metadata.

        :param country_code: The country code from the URN
        :type country_code: str
        :param document_type: The document type from the URN
        :type document_type: str
        :param document_value: The NIF value to extract from
        :type document_value: str
        :param nss_parts: The tokenized NSS parts
        :type nss_parts: list[str]
        :return: Dictionary containing NIF-specific metadata
        :rtype: dict[str, Any]
        """
        value_upper = document_value.upper()

        # Try NIE format first
        nie_match = self._NIE_PATTERN.match(value_upper)
        if nie_match:
            prefix, number_str, check_letter = nie_match.groups()
            return {
                "format_type": "nie",
                "prefix": prefix.upper(),
                "number": number_str,
                "check_letter": check_letter.upper(),
                "generation": self._PREFIX_DESCRIPTIONS.get(prefix.upper(), "Unknown"),
                "document_purpose": "Tax identification number (NIF) using NIE format",
                "is_valid_format": True,
            }

        # Try DNI format
        dni_match = self._DNI_PATTERN.match(value_upper)
        if dni_match:
            number_str, check_letter = dni_match.groups()
            return {
                "format_type": "dni",
                "number": number_str,
                "check_letter": check_letter.upper(),
                "document_purpose": "Tax identification number (NIF) using DNI format",
                "is_valid_format": True,
            }

        raise ValueError(f"Invalid NIF format: {document_value}")


__all__ = ["NIFExtractor"]
