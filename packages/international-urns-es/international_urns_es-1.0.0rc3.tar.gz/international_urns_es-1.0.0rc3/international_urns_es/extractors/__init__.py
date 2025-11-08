"""Extractors for Spanish URN document types."""

from international_urns_es.extractors.cif import CIFExtractor
from international_urns_es.extractors.dir3 import DIR3Extractor
from international_urns_es.extractors.dni import DNIExtractor
from international_urns_es.extractors.nie import NIEExtractor
from international_urns_es.extractors.nif import NIFExtractor
from international_urns_es.extractors.nss import NSSExtractor
from international_urns_es.extractors.plate import PlateExtractor

__all__ = [
    "CIFExtractor",
    "DIR3Extractor",
    "DNIExtractor",
    "NIEExtractor",
    "NIFExtractor",
    "NSSExtractor",
    "PlateExtractor",
]
