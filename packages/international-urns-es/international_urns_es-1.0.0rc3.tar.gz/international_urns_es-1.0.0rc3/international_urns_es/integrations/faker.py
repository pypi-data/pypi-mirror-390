"""Faker integration for Spanish URN generators.

This module provides a Faker provider for generating Spanish URNs.
The provider can be added to Faker instances to enable URN generation.

Example:
    >>> from faker import Faker
    >>> from international_urns_es.integrations.faker import SpanishURNProvider
    >>>
    >>> fake = Faker()
    >>> fake.add_provider(SpanishURNProvider)
    >>>
    >>> # Generate various Spanish URNs
    >>> dni = fake.dni_urn()
    >>> nie = fake.nie_urn()
    >>> cif = fake.cif_urn()
"""

try:
    from faker.providers import BaseProvider
except ImportError as e:
    msg = (
        "Faker is required to use the faker integration. "
        "Install it with: pip install 'international-urns-es[faker]'"
    )
    raise ImportError(msg) from e

import international_urns as iurns


class SpanishURNProvider(BaseProvider):
    """Faker provider for generating Spanish URNs.

    This provider adds methods to Faker instances for generating
    valid Spanish URN strings for various document types.

    Methods:
        dni_urn: Generate a DNI URN
        nie_urn: Generate a NIE URN
        nif_urn: Generate a NIF URN
        cif_urn: Generate a CIF URN
        dir3_urn: Generate a DIR3 URN
        nss_urn: Generate a NSS URN
        plate_urn: Generate a license plate URN
        matricula_urn: Generate a license plate URN (alternative name)
    """

    def dni_urn(self) -> str:
        """Generate a random valid DNI URN.

        :return: A valid DNI URN (e.g., urn:es:dni:12345678Z)
        :rtype: str
        """
        return iurns.get_generator("es", "dni")()  # type: ignore[no-any-return]

    def nie_urn(self) -> str:
        """Generate a random valid NIE URN.

        :return: A valid NIE URN (e.g., urn:es:nie:X1234567L)
        :rtype: str
        """
        return iurns.get_generator("es", "nie")()  # type: ignore[no-any-return]

    def nif_urn(self) -> str:
        """Generate a random valid NIF URN.

        :return: A valid NIF URN (e.g., urn:es:nif:12345678Z)
        :rtype: str
        """
        return iurns.get_generator("es", "nif")()  # type: ignore[no-any-return]

    def cif_urn(self) -> str:
        """Generate a random valid CIF URN.

        :return: A valid CIF URN (e.g., urn:es:cif:A12345674)
        :rtype: str
        """
        return iurns.get_generator("es", "cif")()  # type: ignore[no-any-return]

    def dir3_urn(self) -> str:
        """Generate a random valid DIR3 URN.

        :return: A valid DIR3 URN (e.g., urn:es:dir3:A01002844)
        :rtype: str
        """
        return iurns.get_generator("es", "dir3")()  # type: ignore[no-any-return]

    def nss_urn(self) -> str:
        """Generate a random valid NSS URN.

        :return: A valid NSS URN (e.g., urn:es:nss:281234567840)
        :rtype: str
        """
        return iurns.get_generator("es", "nss")()  # type: ignore[no-any-return]

    def plate_urn(self) -> str:
        """Generate a random valid license plate URN.

        :return: A valid plate URN (e.g., urn:es:plate:1234BBC)
        :rtype: str
        """
        return iurns.get_generator("es", "plate")()  # type: ignore[no-any-return]

    def matricula_urn(self) -> str:
        """Generate a random valid license plate URN (alternative name).

        :return: A valid plate URN (e.g., urn:es:matricula:1234BBC)
        :rtype: str
        """
        return iurns.get_generator("es", "matricula")()  # type: ignore[no-any-return]


__all__ = ["SpanishURNProvider"]
