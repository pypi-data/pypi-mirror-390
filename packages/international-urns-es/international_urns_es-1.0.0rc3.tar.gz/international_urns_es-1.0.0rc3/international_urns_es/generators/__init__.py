"""Spanish URN generators.

This module exports all generator callables for Spanish documents.
"""

from international_urns_es.generators.cif import generate_cif
from international_urns_es.generators.dir3 import generate_dir3
from international_urns_es.generators.dni import generate_dni
from international_urns_es.generators.nie import generate_nie
from international_urns_es.generators.nif import generate_nif
from international_urns_es.generators.nss import generate_nss
from international_urns_es.generators.plate import generate_plate

__all__ = [
    "generate_cif",
    "generate_dir3",
    "generate_dni",
    "generate_nie",
    "generate_nif",
    "generate_nss",
    "generate_plate",
]
