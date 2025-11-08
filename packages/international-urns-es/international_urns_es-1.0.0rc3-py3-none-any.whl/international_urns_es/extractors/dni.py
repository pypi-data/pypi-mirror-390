"""DNI (Documento Nacional de Identidad) extractor for Spain.

Extracts metadata from DNI URNs.
"""

import re
from typing import Any, ClassVar

from international_urns import URNExtractor


class DNIExtractor(URNExtractor):
    """Extractor for Spanish DNI (Documento Nacional de Identidad).

    Extracts the following metadata from DNI URNs:
    - number: The 8-digit number portion
    - check_letter: The check letter
    - document_purpose: Purpose of the document
    - issuing_authority: The issuing authority
    - is_valid_format: Whether the format is valid (always True for extracted URNs)

    Base fields (automatically included):
    - country_code: 'es'
    - document_type: 'dni'
    - document_value: The full DNI value (e.g., '12345678Z')

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["dni"]

    _DNI_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^(\d{8})([A-Z])$", re.IGNORECASE)

    def _extract_metadata(
        self,
        country_code: str,
        document_type: str,
        document_value: str,
        nss_parts: list[str],
    ) -> dict[str, Any]:
        """Extract DNI-specific metadata.

        :param country_code: The country code from the URN
        :type country_code: str
        :param document_type: The document type from the URN
        :type document_type: str
        :param document_value: The DNI value to extract from
        :type document_value: str
        :param nss_parts: The tokenized NSS parts
        :type nss_parts: list[str]
        :return: Dictionary containing DNI-specific metadata
        :rtype: dict[str, Any]
        """
        # Extract DNI components
        value_upper = document_value.upper()
        match = self._DNI_PATTERN.match(value_upper)

        if not match:
            raise ValueError(f"Invalid DNI format: {document_value}")

        number_str, check_letter = match.groups()

        return {
            "number": number_str,
            "check_letter": check_letter.upper(),
            "document_purpose": "National identity document for Spanish citizens",
            "issuing_authority": "Ministerio del Interior",
            "is_valid_format": True,
        }


__all__ = ["DNIExtractor"]
