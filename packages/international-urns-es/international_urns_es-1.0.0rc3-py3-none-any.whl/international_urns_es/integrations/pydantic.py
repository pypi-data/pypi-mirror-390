"""Pydantic integration for Spanish URN validators.

This module provides convenient type aliases using Pydantic's AfterValidator
for all Spanish URN types. These can be used directly in Pydantic models.

Example:
    >>> from typing import Annotated
    >>> from pydantic import BaseModel
    >>> from international_urns_es.integrations.pydantic import DNI_URN, CIF_URN
    >>>
    >>> class Person(BaseModel):
    ...     name: str
    ...     dni: DNI_URN
    >>>
    >>> person = Person(name="John Doe", dni="urn:es:dni:12345678Z")
"""

from typing import Annotated

try:
    from pydantic import AfterValidator
except ImportError as e:
    msg = (
        "Pydantic is required to use the pydantic integration. "
        "Install it with: pip install 'international-urns-es[pydantic]'"
    )
    raise ImportError(msg) from e

import international_urns as iurns

# Type aliases for all Spanish URN types using AfterValidator
DNI_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "dni"))]
"""Type alias for DNI URNs validated with Pydantic AfterValidator."""

NIE_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "nie"))]
"""Type alias for NIE URNs validated with Pydantic AfterValidator."""

NIF_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "nif"))]
"""Type alias for NIF URNs validated with Pydantic AfterValidator."""

CIF_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "cif"))]
"""Type alias for CIF URNs validated with Pydantic AfterValidator."""

DIR3_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "dir3"))]
"""Type alias for DIR3 URNs validated with Pydantic AfterValidator."""

NSS_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "nss"))]
"""Type alias for NSS URNs validated with Pydantic AfterValidator."""

PLATE_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "plate"))]
"""Type alias for license plate URNs validated with Pydantic AfterValidator."""

MATRICULA_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "matricula"))]
"""Type alias for license plate URNs (matricula) validated with Pydantic AfterValidator."""


__all__ = [
    "DNI_URN",
    "NIE_URN",
    "NIF_URN",
    "CIF_URN",
    "DIR3_URN",
    "NSS_URN",
    "PLATE_URN",
    "MATRICULA_URN",
]
