"""NIE (Número de Identidad de Extranjero) extractor for Spain.

Extracts metadata from NIE URNs.
"""

import re
from typing import Any, ClassVar

from international_urns import URNExtractor


class NIEExtractor(URNExtractor):
    """Extractor for Spanish NIE (Número de Identidad de Extranjero).

    Extracts the following metadata from NIE URNs:
    - prefix: The prefix letter (X, Y, or Z)
    - number: The 7-digit number portion
    - check_letter: The check letter
    - generation: Description of what the prefix represents with historical context
    - document_purpose: Purpose of the document
    - format_history: Historical information about format changes
    - is_valid_format: Whether the format is valid (always True for extracted URNs)

    Base fields (automatically included):
    - country_code: 'es'
    - document_type: 'nie'
    - document_value: The full NIE value (e.g., 'X1234567L')

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["nie"]

    _NIE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([XYZ])(\d{7})([A-Z])$", re.IGNORECASE)

    # Generation mappings for prefix letters with historical context
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
        """Extract NIE-specific metadata.

        :param country_code: The country code from the URN
        :type country_code: str
        :param document_type: The document type from the URN
        :type document_type: str
        :param document_value: The NIE value to extract from
        :type document_value: str
        :param nss_parts: The tokenized NSS parts
        :type nss_parts: list[str]
        :return: Dictionary containing NIE-specific metadata
        :rtype: dict[str, Any]
        """
        # Extract NIE components
        value_upper = document_value.upper()
        match = self._NIE_PATTERN.match(value_upper)

        if not match:
            raise ValueError(f"Invalid NIE format: {document_value}")

        prefix, number_str, check_letter = match.groups()

        return {
            "prefix": prefix.upper(),
            "number": number_str,
            "check_letter": check_letter.upper(),
            "generation": self._PREFIX_DESCRIPTIONS.get(prefix.upper(), "Unknown"),
            "document_purpose": "Identification number for foreign nationals in Spain",
            "format_history": "Format changed from 8 to 7 digits by Orden INT/2058/2008",
            "is_valid_format": True,
        }


__all__ = ["NIEExtractor"]
