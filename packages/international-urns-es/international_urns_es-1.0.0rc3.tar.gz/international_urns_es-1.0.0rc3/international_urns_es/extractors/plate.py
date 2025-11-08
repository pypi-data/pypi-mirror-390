"""Spanish vehicle license plate extractor.

Extracts metadata from license plate URNs including format detection.
"""

import re
from typing import Any, ClassVar

from international_urns import URNExtractor


class PlateExtractor(URNExtractor):
    """Extractor for Spanish vehicle license plates.

    Extracts the following metadata from license plate URNs:
    - plate_format: Format type ('current', 'old', or 'special')
    - digits: The numeric portion
    - letters: The letter portion
    - province_code: Province code (only for old format)
    - province_name: Province name (only for old format, if known)
    - special_type: Type of special plate (only for special format)
    - special_type_description: Description of special plate type
    - is_valid_format: Whether the format is valid

    Base fields (automatically included):
    - country_code: 'es'
    - document_type: 'plate' or 'matricula'
    - document_value: The full plate value

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["plate", "matricula"]

    # Current format: 4 digits + 3 consonants
    _CURRENT_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^(\d{4})([BCDFGHJKLMNPRSTVWXYZ]{3})$", re.IGNORECASE
    )

    # Old format: 1-2 letters + 4 digits + 1-2 letters
    _OLD_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^([A-Z]{1,2})(\d{4})([A-Z]{1,2})$", re.IGNORECASE
    )

    # Special formats
    _SPECIAL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^(CD|CC|E|ET|CMD|DGP|MF|MMA|PMM|CNP)(\d{4,5})$", re.IGNORECASE
    )

    # Province code mappings for old format
    _PROVINCE_CODES: ClassVar[dict[str, str]] = {
        "A": "Alicante",
        "AB": "Albacete",
        "AL": "Almería",
        "AV": "Ávila",
        "B": "Barcelona",
        "BA": "Badajoz",
        "BI": "Vizcaya",
        "BU": "Burgos",
        "C": "A Coruña",
        "CA": "Cádiz",
        "CC": "Cáceres",
        "CE": "Ceuta",
        "CO": "Córdoba",
        "CR": "Ciudad Real",
        "CS": "Castellón",
        "CU": "Cuenca",
        "GC": "Las Palmas",
        "GI": "Girona",
        "GR": "Granada",
        "GU": "Guadalajara",
        "H": "Huelva",
        "HU": "Huesca",
        "J": "Jaén",
        "L": "Lleida",
        "LE": "León",
        "LO": "La Rioja",
        "LU": "Lugo",
        "M": "Madrid",
        "MA": "Málaga",
        "ML": "Melilla",
        "MU": "Murcia",
        "NA": "Navarra",
        "O": "Asturias",
        "OR": "Ourense",
        "P": "Palencia",
        "PM": "Baleares",
        "PO": "Pontevedra",
        "S": "Cantabria",
        "SA": "Salamanca",
        "SE": "Sevilla",
        "SG": "Segovia",
        "SO": "Soria",
        "SS": "Guipúzcoa",
        "T": "Tarragona",
        "TE": "Teruel",
        "TF": "Santa Cruz de Tenerife",
        "TO": "Toledo",
        "V": "Valencia",
        "VA": "Valladolid",
        "VI": "Álava",
        "Z": "Zaragoza",
        "ZA": "Zamora",
    }

    # Special plate type descriptions
    _SPECIAL_TYPES: ClassVar[dict[str, str]] = {
        "CD": "Cuerpo Diplomático (Diplomatic Corps)",
        "CC": "Cuerpo Consular (Consular Corps)",
        "E": "Extranjero (Foreign)",
        "ET": "Extranjero Temporal (Temporary Foreign)",
        "CMD": "Casa de Su Majestad el Rey (Royal Household)",
        "DGP": "Dirección General de Policía (Police Directorate)",
        "MF": "Ministerio de Defensa - Fuerzas Armadas (Ministry of Defense - Armed Forces)",
        "MMA": "Ministerio de Medio Ambiente (Ministry of Environment)",
        "PMM": "Parque Móvil del Estado (State Vehicle Pool)",
        "CNP": "Cuerpo Nacional de Policía (National Police Corps)",
    }

    def _extract_metadata(
        self,
        country_code: str,
        document_type: str,
        document_value: str,
        nss_parts: list[str],
    ) -> dict[str, Any]:
        """Extract license plate-specific metadata.

        :param country_code: The country code from the URN
        :type country_code: str
        :param document_type: The document type from the URN
        :type document_type: str
        :param document_value: The plate value to extract from
        :type document_value: str
        :param nss_parts: The tokenized NSS parts
        :type nss_parts: list[str]
        :return: Dictionary containing plate-specific metadata
        :rtype: dict[str, Any]
        """
        # Remove spaces and hyphens, convert to uppercase
        plate = document_value.replace(" ", "").replace("-", "").upper()

        # Try current format
        current_match = self._CURRENT_PATTERN.match(plate)
        if current_match:
            digits, letters = current_match.groups()
            return {
                "plate_format": "current",
                "digits": digits,
                "letters": letters.upper(),
                "is_valid_format": True,
            }

        # Try old format
        old_match = self._OLD_PATTERN.match(plate)
        if old_match:
            province_code, digits, letters = old_match.groups()
            province_code = province_code.upper()
            province_name = self._PROVINCE_CODES.get(province_code, "Unknown")
            return {
                "plate_format": "old",
                "province_code": province_code,
                "province_name": province_name,
                "digits": digits,
                "letters": letters.upper(),
                "is_valid_format": True,
            }

        # Try special formats
        special_match = self._SPECIAL_PATTERN.match(plate)
        if special_match:
            special_type, digits = special_match.groups()
            special_type = special_type.upper()
            special_description = self._SPECIAL_TYPES.get(special_type, "Unknown special type")
            return {
                "plate_format": "special",
                "special_type": special_type,
                "special_type_description": special_description,
                "digits": digits,
                "is_valid_format": True,
            }

        raise ValueError(f"Invalid license plate format: {document_value}")


__all__ = ["PlateExtractor"]
