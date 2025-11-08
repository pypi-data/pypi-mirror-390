"""CIF (Código de Identificación Fiscal) extractor for Spain.

Extracts metadata from CIF URNs including organization type detection.
"""

import re
from typing import Any, ClassVar

from international_urns import URNExtractor


class CIFExtractor(URNExtractor):
    """Extractor for Spanish CIF (Código de Identificación Fiscal).

    Extracts the following metadata from CIF URNs:
    - organization_type_code: The organization type letter (A-W)
    - organization_type_name: Full name of the organization type
    - organization_category: Category (legal_entity, public_entity, or religious)
    - number: The 7-digit number portion
    - check_character: The check digit/letter
    - check_format: Whether check is 'digit' or 'letter'
    - provincial_code: The province code (first 2 digits of number)
    - is_valid_format: Whether the format is valid

    Base fields (automatically included):
    - country_code: 'es'
    - document_type: 'cif'
    - document_value: The full CIF value

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["cif"]

    _CIF_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^([A-HJNPQRSUVW])(\d{7})([A-J0-9])$", re.IGNORECASE
    )

    # Organization type mappings
    _ORGANIZATION_TYPES: ClassVar[dict[str, tuple[str, str]]] = {
        "A": ("Sociedad Anónima", "legal_entity"),
        "B": ("Sociedad de Responsabilidad Limitada", "legal_entity"),
        "C": ("Sociedad Colectiva", "legal_entity"),
        "D": ("Sociedad Comanditaria", "legal_entity"),
        "E": ("Comunidad de Bienes", "legal_entity"),
        "F": ("Sociedad Cooperativa", "legal_entity"),
        "G": ("Asociación", "legal_entity"),
        "H": ("Comunidad de Propietarios", "legal_entity"),
        "J": ("Sociedad Civil", "legal_entity"),
        "N": ("Entidad Extranjera", "legal_entity"),
        "P": ("Corporación Local", "public_entity"),
        "Q": ("Organismo Autónomo", "public_entity"),
        "R": ("Congregación o Institución Religiosa", "religious"),
        "S": ("Órgano de la Administración del Estado", "public_entity"),
        "U": ("Unión Temporal de Empresas", "legal_entity"),
        "V": ("Otro tipo no definido", "legal_entity"),
        "W": ("Establecimiento Permanente de Entidad No Residente", "legal_entity"),
    }

    # Organization types that must have a letter as check digit
    _LETTER_CHECK_TYPES: ClassVar[set[str]] = {"N", "P", "Q", "R", "S", "W"}

    # Organization types that must have a number as check digit
    _NUMBER_CHECK_TYPES: ClassVar[set[str]] = {"A", "B", "E", "H"}

    # Province code mappings (using same codes as NSS)
    _PROVINCE_NAMES: ClassVar[dict[str, str]] = {
        "01": "Álava",
        "02": "Albacete",
        "03": "Alicante",
        "04": "Almería",
        "05": "Ávila",
        "06": "Badajoz",
        "07": "Baleares",
        "08": "Barcelona",
        "09": "Burgos",
        "10": "Cáceres",
        "11": "Cádiz",
        "12": "Castellón",
        "13": "Ciudad Real",
        "14": "Córdoba",
        "15": "A Coruña",
        "16": "Cuenca",
        "17": "Girona",
        "18": "Granada",
        "19": "Guadalajara",
        "20": "Guipúzcoa",
        "21": "Huelva",
        "22": "Huesca",
        "23": "Jaén",
        "24": "León",
        "25": "Lleida",
        "26": "La Rioja",
        "27": "Lugo",
        "28": "Madrid",
        "29": "Málaga",
        "30": "Murcia",
        "31": "Navarra",
        "32": "Ourense",
        "33": "Asturias",
        "34": "Palencia",
        "35": "Las Palmas",
        "36": "Pontevedra",
        "37": "Salamanca",
        "38": "Santa Cruz de Tenerife",
        "39": "Cantabria",
        "40": "Segovia",
        "41": "Sevilla",
        "42": "Soria",
        "43": "Tarragona",
        "44": "Teruel",
        "45": "Toledo",
        "46": "Valencia",
        "47": "Valladolid",
        "48": "Vizcaya",
        "49": "Zamora",
        "50": "Zaragoza",
        "51": "Ceuta",
        "52": "Melilla",
    }

    def _extract_metadata(
        self,
        country_code: str,
        document_type: str,
        document_value: str,
        nss_parts: list[str],
    ) -> dict[str, Any]:
        """Extract CIF-specific metadata.

        :param country_code: The country code from the URN
        :type country_code: str
        :param document_type: The document type from the URN
        :type document_type: str
        :param document_value: The CIF value to extract from
        :type document_value: str
        :param nss_parts: The tokenized NSS parts
        :type nss_parts: list[str]
        :return: Dictionary containing CIF-specific metadata
        :rtype: dict[str, Any]
        """
        value_upper = document_value.upper()
        match = self._CIF_PATTERN.match(value_upper)

        if not match:
            raise ValueError(f"Invalid CIF format: {document_value}")

        org_type, number_str, check_char = match.groups()
        org_type = org_type.upper()
        check_char = check_char.upper()

        # Get organization type information
        org_name, org_category = self._ORGANIZATION_TYPES.get(org_type, ("Unknown", "unknown"))

        # Determine check character format
        if check_char.isdigit():
            check_format = "digit"
        else:
            check_format = "letter"

        # Extract provincial code (first 2 digits)
        provincial_code = number_str[:2]
        provincial_name = self._PROVINCE_NAMES.get(provincial_code, "Unknown")

        return {
            "organization_type_code": org_type,
            "organization_type_name": org_name,
            "organization_category": org_category,
            "number": number_str,
            "check_character": check_char,
            "check_format": check_format,
            "provincial_code": provincial_code,
            "provincial_name": provincial_name,
            "is_valid_format": True,
        }


__all__ = ["CIFExtractor"]
