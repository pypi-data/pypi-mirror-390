"""NSS (Número de la Seguridad Social) validator for Spain.

The NSS is the Social Security Number used in Spain.
Format: 12 digits in the pattern XX/XXXXXXXXXX/XX or as a continuous 12-digit number.
Example: 281234567840 or 28/12345678/40
"""

import re
from typing import ClassVar

from international_urns import URNValidator


class NSSValidator(URNValidator):
    """Validator for Spanish NSS (Número de la Seguridad Social).

    The NSS consists of 12 digits that can be formatted with or without slashes:
    - With slashes: XX/XXXXXXXXXX/XX (e.g., 28/12345678/40)
    - Without slashes: XXXXXXXXXXXX (e.g., 281234567840)

    Structure:
    - First 2 digits: Province code (01-52 or special codes 66-99)
    - Next 8 digits: Sequential number
    - Last 2 digits: Check digits

    Valid formats:
    - urn:es:nss:281234567840
    - urn:es:nss:28/12345678/40

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["nss"]

    # Pattern with slashes
    _NSS_PATTERN_SLASHES: ClassVar[re.Pattern[str]] = re.compile(r"^(\d{2})/(\d{8})/(\d{2})$")
    # Pattern without slashes
    _NSS_PATTERN_NO_SLASHES: ClassVar[re.Pattern[str]] = re.compile(r"^(\d{12})$")

    def validate(self, urn: str) -> str:
        """Validate a Spanish NSS URN.

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

        # Validate NSS format and check digits
        self._validate_nss(value)

        # Return normalized URN (lowercase scheme, country, and doc_type)
        return f"urn:{country.lower()}:{doc_type.lower()}:{value}"

    def _validate_nss(self, nss: str) -> None:
        """Validate NSS format and check digits.

        :param nss: The NSS value to validate
        :type nss: str
        :raises ValueError: If the NSS is invalid
        """
        # Try pattern with slashes first
        match_slashes = self._NSS_PATTERN_SLASHES.match(nss)
        if match_slashes:
            province, sequential, check = match_slashes.groups()
            nss_digits = province + sequential + check
        else:
            # Try pattern without slashes
            match_no_slashes = self._NSS_PATTERN_NO_SLASHES.match(nss)
            if match_no_slashes:
                nss_digits = match_no_slashes.group(1)
                province = nss_digits[0:2]
                sequential = nss_digits[2:10]
                check = nss_digits[10:12]
            else:
                raise ValueError(
                    f"Invalid NSS format: {nss}. "
                    "Expected 12 digits (optionally formatted as XX/XXXXXXXX/XX)"
                )

        # Validate province code
        province_code = int(province)
        if not (1 <= province_code <= 52 or 66 <= province_code <= 99):
            raise ValueError(f"Invalid NSS province code: {province}. Expected 01-52 or 66-99")

        # Validate check digits
        self._validate_check_digits(province + sequential, check)

    def _validate_check_digits(self, base: str, check: str) -> None:
        """Validate NSS check digits.

        The check digits are calculated as: (base number) mod 97

        :param base: The first 10 digits (province + sequential)
        :type base: str
        :param check: The check digits (last 2 digits)
        :type check: str
        :raises ValueError: If check digits are invalid
        """
        base_number = int(base)
        expected_check = base_number % 97
        actual_check = int(check)

        if expected_check != actual_check:
            raise ValueError(
                f"Invalid NSS check digits. Expected {expected_check:02d}, got {check}"
            )


__all__ = ["NSSValidator"]
