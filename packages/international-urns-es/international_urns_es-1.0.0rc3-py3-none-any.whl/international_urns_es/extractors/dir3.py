"""DIR3 (Directorio Común) extractor for Spain.

Extracts metadata from DIR3 URNs including administration level detection.
"""

import re
from typing import Any, ClassVar

from international_urns import URNExtractor


class DIR3Extractor(URNExtractor):
    """Extractor for Spanish DIR3 (Directorio Común) codes.

    Extracts the following metadata from DIR3 URNs:
    - administration_level_code: The administration level prefix (E, A, L, U, I, J, O, GE, EC, EA)
    - administration_level_name: Full name of the administration level
    - unit_code: The numeric identifier (7-8 digits depending on prefix)
    - For A codes: autonomous_community_code and autonomous_community_name
    - For L codes: geographic_entity_code and geographic_entity_name
    - For U codes: university_siiu_code (3-digit SIIU code assigned by Ministry of Education)
    - is_valid_format: Whether the format is valid

    Base fields (automatically included):
    - country_code: 'es'
    - document_type: 'dir3'
    - document_value: The full DIR3 value

    :cvar country_code: ISO 3166-1 Alpha-2 code for Spain
    :cvar document_types: List of supported document type identifiers
    """

    country_code: ClassVar[str] = "es"
    document_types: ClassVar[list[str]] = ["dir3"]

    _DIR3_PATTERN_SINGLE: ClassVar[re.Pattern[str]] = re.compile(
        r"^([EALUIJO])(\d{8})$", re.IGNORECASE
    )
    _DIR3_PATTERN_DOUBLE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(GE|EC|EA)(\d{7})$", re.IGNORECASE
    )

    # Administration level mappings
    _ADMIN_LEVELS: ClassVar[dict[str, str]] = {
        "E": "Administración del Estado",
        "A": "Administración Autonómica",
        "L": "Administración Local",
        "U": "Universidades",
        "I": "Otras Instituciones",
        "J": "Administración de Justicia",
        "O": "Oficinas",
        "GE": "Unidad de Gestión Económica-Presupuestaria",
        "EC": "Entidades Colaboradoras",
        "EA": "Administración del Estado (no RCP)",
    }

    # Autonomous communities catalog (code INE)
    _AUTONOMOUS_COMMUNITIES: ClassVar[dict[str, str]] = {
        "01": "Andalucía",
        "02": "Aragón",
        "03": "Principado de Asturias",
        "04": "Illes Balears",
        "05": "Canarias",
        "06": "Cantabria",
        "07": "Castilla y León",
        "08": "Castilla-La Mancha",
        "09": "Cataluña",
        "10": "Comunitat Valenciana",
        "11": "Extremadura",
        "12": "Galicia",
        "13": "Comunidad de Madrid",
        "14": "Región de Murcia",
        "15": "Comunidad Foral de Navarra",
        "16": "País Vasco",
        "17": "La Rioja",
        "18": "Ciudad de Ceuta",
        "19": "Ciudad de Melilla",
    }

    # Geographic entity types catalog
    _GEOGRAPHIC_ENTITIES: ClassVar[dict[str, str]] = {
        "01": "Municipio",
        "02": "Provincia",
        "03": "Isla",
        "04": "Entidad Local Menor",
        "05": "Mancomunidad",
        "06": "Comarca",
        "07": "Área Metropolitana",
        "08": "Otras Agrupaciones",
        "10": "País",
        "20": "Comunidad Autónoma",
        "00": "SIN DATO",
    }

    def _extract_metadata(
        self,
        country_code: str,
        document_type: str,
        document_value: str,
        nss_parts: list[str],
    ) -> dict[str, Any]:
        """Extract DIR3-specific metadata.

        :param country_code: The country code from the URN
        :type country_code: str
        :param document_type: The document type from the URN
        :type document_type: str
        :param document_value: The DIR3 value to extract from
        :type document_value: str
        :param nss_parts: The tokenized NSS parts
        :type nss_parts: list[str]
        :return: Dictionary containing DIR3-specific metadata
        :rtype: dict[str, Any]
        """
        value_upper = document_value.upper()

        # Try single-letter prefix first
        match_single = self._DIR3_PATTERN_SINGLE.match(value_upper)
        if match_single:
            prefix, unit_code = match_single.groups()
            prefix = prefix.upper()
            admin_name = self._ADMIN_LEVELS.get(prefix, "Unknown")

            result: dict[str, Any] = {
                "administration_level_code": prefix,
                "administration_level_name": admin_name,
                "unit_code": unit_code,
                "is_valid_format": True,
            }

            # Extract additional info for Autonomous Administration (A)
            if prefix == "A" and len(unit_code) >= 2:
                ca_code = unit_code[0:2]
                ca_name = self._AUTONOMOUS_COMMUNITIES.get(ca_code, "Unknown")
                result["autonomous_community_code"] = ca_code
                result["autonomous_community_name"] = ca_name

            # Extract additional info for Local Administration (L)
            elif prefix == "L" and len(unit_code) >= 2:
                eg_code = unit_code[0:2]
                eg_name = self._GEOGRAPHIC_ENTITIES.get(eg_code, "Unknown")
                result["geographic_entity_code"] = eg_code
                result["geographic_entity_name"] = eg_name

            # Extract additional info for Universities (U)
            elif prefix == "U" and len(unit_code) >= 3:
                siiu_code = unit_code[0:3]
                result["university_siiu_code"] = siiu_code

            return result

        # Try double-letter prefix
        match_double = self._DIR3_PATTERN_DOUBLE.match(value_upper)
        if match_double:
            prefix, unit_code = match_double.groups()
            prefix = prefix.upper()
            admin_name = self._ADMIN_LEVELS.get(prefix, "Unknown")

            return {
                "administration_level_code": prefix,
                "administration_level_name": admin_name,
                "unit_code": unit_code,
                "is_valid_format": True,
            }

        raise ValueError(f"Invalid DIR3 format: {document_value}")


__all__ = ["DIR3Extractor"]
