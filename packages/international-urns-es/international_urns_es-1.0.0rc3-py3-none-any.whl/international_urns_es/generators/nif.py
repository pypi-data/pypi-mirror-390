"""NIF (Número de Identificación Fiscal) generator for Spain.

The NIF is the tax identification number for individuals in Spain.
It accepts both DNI and NIE formats.
"""

import random

from international_urns_es.generators.dni import generate_dni
from international_urns_es.generators.nie import generate_nie


def generate_nif() -> str:
    """Generate a random valid NIF URN.

    The NIF can be either a DNI or NIE format. This generator randomly
    selects one of the two formats.

    :return: A valid NIF URN (e.g., urn:es:nif:12345678Z or urn:es:nif:X1234567L)
    :rtype: str
    """
    # Randomly choose between DNI and NIE format
    if random.choice([True, False]):
        # Generate DNI format and convert to NIF
        dni_urn = generate_dni()
        return dni_urn.replace(":dni:", ":nif:")
    else:
        # Generate NIE format and convert to NIF
        nie_urn = generate_nie()
        return nie_urn.replace(":nie:", ":nif:")


__all__ = ["generate_nif"]
