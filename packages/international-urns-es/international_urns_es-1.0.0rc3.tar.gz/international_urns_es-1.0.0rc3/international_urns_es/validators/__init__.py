"""Spanish document validators.

This module exports all validator classes for Spanish documents.
"""

from international_urns_es.validators.cif import CIFValidator
from international_urns_es.validators.dir3 import DIR3Validator
from international_urns_es.validators.dni import DNIValidator
from international_urns_es.validators.nie import NIEValidator
from international_urns_es.validators.nif import NIFValidator
from international_urns_es.validators.nss import NSSValidator
from international_urns_es.validators.plate import PlateValidator

__all__ = [
    "CIFValidator",
    "DIR3Validator",
    "DNIValidator",
    "NIEValidator",
    "NIFValidator",
    "NSSValidator",
    "PlateValidator",
]
