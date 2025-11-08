# International URNs - Spain Plugin

A comprehensive plugin for [International URNs](https://github.com/international-urns/international-urns) that provides validators and generators for Spanish identity documents and administrative codes.

## Requirements

- Python 3.11 or higher
- international-urns 1.0.0rc4 or higher (for extraction support)
- Pydantic 2.0+ (optional, for Pydantic integration)
- Faker 18.0+ (optional, for Faker integration)

## Installation

```bash
# Basic installation
pip install international-urns-es

# With Pydantic integration
pip install international-urns-es[pydantic]

# With Faker integration
pip install international-urns-es[faker]

# With all optional dependencies
pip install international-urns-es[all]
```

## Supported Documents

This plugin validates, generates, and extracts metadata from the following Spanish document types:

- **DNI** - Documento Nacional de Identidad (National Identity Document)
- **NIE** - Número de Identidad de Extranjero (Foreigner Identity Number)
- **NIF** - Número de Identificación Fiscal (Tax Identification Number)
- **CIF** - Código de Identificación Fiscal (Company Tax Code)
- **DIR3** - Directorio Común de unidades y oficinas (Common Directory of Administrative Units)
- **NSS** - Número de la Seguridad Social (Social Security Number)
- **License Plates** - Matrículas de vehículos (Vehicle registration plates)

### Features

- **Validation**: Check if URNs are correctly formatted and valid according to Spanish regulations
- **Generation**: Create random valid URNs for testing purposes
- **Metadata Extraction**: Extract rich metadata from URNs including document purpose, historical context, organization types, administration levels, and more
- **Official Algorithms**: All validators use official algorithms documented in Spanish government regulations

## Quick Start

### Validation

```python
import international_urns as iurns

# Validate a DNI
dni_validator = iurns.get_validator('es', 'dni')
result = dni_validator('urn:es:dni:12345678Z')
print(result)  # urn:es:dni:12345678Z

# Validate a NIE
nie_validator = iurns.get_validator('es', 'nie')
result = nie_validator('urn:es:nie:X1234567L')
print(result)  # urn:es:nie:X1234567L

# Validate a license plate
plate_validator = iurns.get_validator('es', 'plate')
result = plate_validator('urn:es:plate:1234BBC')
print(result)  # urn:es:plate:1234BBC
```

### Generation

```python
import international_urns as iurns

# Generate a random valid DNI
dni_generator = iurns.get_generator('es', 'dni')
dni_urn = dni_generator()
print(dni_urn)  # urn:es:dni:43335678K (random)

# Generate a random valid CIF
cif_generator = iurns.get_generator('es', 'cif')
cif_urn = cif_generator()
print(cif_urn)  # urn:es:cif:B12345670 (random)

# Direct import also works
from international_urns_es import generate_dni, generate_nie

dni_urn = generate_dni()
nie_urn = generate_nie()
```

### Metadata Extraction

Extract rich metadata from URNs:

```python
import international_urns as iurns

# Extract metadata from any URN
metadata = iurns.extract_urn('urn:es:cif:B01234566')

print(metadata['country_code'])              # Output: 'es'
print(metadata['document_type'])             # Output: 'cif'
print(metadata['organization_type_name'])    # Output: 'Sociedad de Responsabilidad Limitada'
print(metadata['organization_category'])     # Output: 'legal_entity'
print(metadata['provincial_code'])           # Output: '01'

# Extract from DIR3
dir3_metadata = iurns.extract_urn('urn:es:dir3:A01002844')
print(dir3_metadata['administration_level_name'])  # Output: 'Administración General del Estado'

# Extract from license plate
plate_metadata = iurns.extract_urn('urn:es:plate:M1234AB')
print(plate_metadata['plate_format'])       # Output: 'old'
print(plate_metadata['province_name'])      # Output: 'Madrid'
```

Each document type provides specific metadata fields. See the [Document Types Reference](#document-types-reference) below for details on what metadata each extractor provides.

## Document Types Reference

### DNI (Documento Nacional de Identidad)

The DNI is the national identity document for Spanish citizens.

**Format:** 8 digits + 1 check letter

**Examples:**
- `12345678Z`
- `00000000T`
- `99999999R`

**URN Format:**
```
urn:es:dni:12345678Z
```

**Usage:**
```python
import international_urns as iurns

validator = iurns.get_validator('es', 'dni')

# Valid DNI
try:
    result = validator('urn:es:dni:12345678Z')
    print(f"Valid: {result}")
except ValueError as e:
    print(f"Invalid: {e}")
```

**Validation Rules:**
- Must be exactly 8 digits followed by 1 letter
- Check letter is calculated using modulo 23 algorithm
- Case-insensitive for URN scheme, country, and document type
- Value preserves original case

**Extracted Metadata:**
```python
metadata = iurns.extract_urn('urn:es:dni:12345678Z')
# Returns:
# {
#     'country_code': 'es',
#     'document_type': 'dni',
#     'document_value': '12345678Z',
#     'number': '12345678',
#     'check_letter': 'Z',
#     'is_valid_format': True
# }
```

---

### NIE (Número de Identidad de Extranjero)

The NIE is the identification number for foreign nationals residing in Spain.

**Format:** Letter (X, Y, or Z) + 7 digits + 1 check letter

**Examples:**
- `X1234567L`
- `Y0000000Z`
- `Z9999999R`

**URN Format:**
```
urn:es:nie:X1234567L
```

**Usage:**
```python
import international_urns as iurns

validator = iurns.get_validator('es', 'nie')
result = validator('urn:es:nie:X1234567L')
```

**Validation Rules:**
- Prefix must be X, Y, or Z
- Followed by exactly 7 digits
- Check letter calculated using same algorithm as DNI (with prefix conversion: X→0, Y→1, Z→2)

**Extracted Metadata:**
```python
metadata = iurns.extract_urn('urn:es:nie:X1234567L')
# Returns:
# {
#     'country_code': 'es',
#     'document_type': 'nie',
#     'document_value': 'X1234567L',
#     'prefix': 'X',
#     'number': '1234567',
#     'check_letter': 'L',
#     'generation': 'Original NIE series, issued until July 15, 2008 (X = 0 for check letter calculation)',
#     'document_purpose': 'Identification number for foreign nationals in Spain',
#     'format_history': 'Format changed from 8 to 7 digits by Orden INT/2058/2008',
#     'is_valid_format': True
# }
```

---

### NIF (Número de Identificación Fiscal)

The NIF is the tax identification number for individuals in Spain. It accepts both DNI and NIE formats.

**Format:** DNI format (8 digits + letter) or NIE format (letter + 7 digits + letter)

**Examples:**
- `12345678Z` (DNI format)
- `X1234567L` (NIE format)

**URN Format:**
```
urn:es:nif:12345678Z
urn:es:nif:X1234567L
```

**Usage:**
```python
import international_urns as iurns

validator = iurns.get_validator('es', 'nif')

# DNI format
result1 = validator('urn:es:nif:12345678Z')

# NIE format
result2 = validator('urn:es:nif:X1234567L')
```

**Validation Rules:**
- Accepts both DNI and NIE formats
- Validates check letter for both formats

**Extracted Metadata:**
```python
# For DNI format
metadata = iurns.extract_urn('urn:es:nif:12345678Z')
# Returns: {'format_type': 'dni', 'number': '12345678', 'check_letter': 'Z', ...}

# For NIE format
metadata = iurns.extract_urn('urn:es:nif:X1234567L')
# Returns: {'format_type': 'nie', 'prefix': 'X', 'number': '1234567',
#           'generation': '...', ...}
```

---

### CIF (Código de Identificación Fiscal)

The CIF is the tax identification code for Spanish companies and organizations.

**Format:** 1 organization letter + 7 digits + 1 check character (letter or digit)

**Organization Type Letters:**
- **A** - Sociedades Anónimas (Public Limited Companies)
- **B** - Sociedades de Responsabilidad Limitada (Private Limited Companies)
- **C** - Sociedades Colectivas (General Partnerships)
- **D** - Sociedades Comanditarias (Limited Partnerships)
- **E** - Comunidades de Bienes (Communities of Property)
- **F** - Sociedades Cooperativas (Cooperatives)
- **G** - Asociaciones (Associations)
- **H** - Comunidades de Propietarios (Homeowner Associations)
- **J** - Sociedades Civiles (Civil Partnerships)
- **N** - Entidades Extranjeras (Foreign Entities)
- **P** - Corporaciones Locales (Local Corporations)
- **Q** - Organismos Autónomos (Autonomous Bodies)
- **R** - Congregaciones e Instituciones Religiosas (Religious Organizations)
- **S** - Órganos de la Administración del Estado (State Administration Bodies)
- **U** - Uniones Temporales de Empresas (Temporary Business Associations)
- **V** - Otros tipos no definidos (Other Undefined Types)
- **W** - Establecimientos permanentes de entidades no residentes (Permanent Establishments)

**Examples:**
- `A12345674` (SA - Sociedad Anónima, check digit is number)
- `B01234566` (SL - Sociedad Limitada, check digit is number)
- `N1234567J` (Foreign entity - check digit is letter)

**URN Format:**
```
urn:es:cif:A12345674
```

**Usage:**
```python
import international_urns as iurns

validator = iurns.get_validator('es', 'cif')
result = validator('urn:es:cif:A12345674')
```

**Validation Rules:**
- Organization types N, P, Q, R, S, W must have a letter as check digit
- Organization types A, B, E, H must have a number as check digit
- Other types can have either
- Check digit calculated using weighted sum algorithm

**Extracted Metadata:**
```python
metadata = iurns.extract_urn('urn:es:cif:B01234566')
# Returns:
# {
#     'country_code': 'es',
#     'document_type': 'cif',
#     'document_value': 'B01234566',
#     'organization_type_code': 'B',
#     'organization_type_name': 'Sociedad de Responsabilidad Limitada',
#     'organization_category': 'legal_entity',  # or 'public_entity', 'religious'
#     'number': '0123456',
#     'check_character': '6',
#     'check_format': 'digit',  # or 'letter'
#     'provincial_code': '01',
#     'provincial_name': 'Álava',
#     'is_valid_format': True
# }
```

---

### DIR3 (Directorio Común)

DIR3 codes identify administrative units and offices in the Spanish Public Administration.

**Format:** Exactly **9 alphanumeric characters**
- Single-letter prefix (E, A, L, U, I, J, O) + 8 digits
- Double-letter prefix (EA, GE, EC) + 7 digits

**Administration Level Codes:**

*Single-letter prefixes:*
- **E** - Administración del Estado (State Administration)
- **A** - Administración Autonómica (Autonomous Community Administration)
- **L** - Administración Local (Local Administration)
- **U** - Universidades (Universities)
- **I** - Otras Instituciones (Other Institutions)
- **J** - Administración de Justicia (Justice Administration)
- **O** - Oficinas (Offices)

*Double-letter prefixes:*
- **EA** - Administración del Estado no RCP (State Administration, non-RCP)
- **GE** - Unidad de Gestión Económica-Presupuestaria (Economic-Budgetary Management Unit)
- **EC** - Entidades Colaboradoras (Collaborating Entities)

**Examples:**
- `E00010201` (State administration unit)
- `A13000001` (Autonomous community - Madrid)
- `L01234567` (Local administration - Municipality)
- `U00112345` (University)
- `EA0043247` (State administration - non-RCP)
- `GE0001234` (Economic management unit)
- `EC0005678` (Collaborating entity)

**URN Format:**
```
urn:es:dir3:E00010201
urn:es:dir3:A13000001
urn:es:dir3:EA0043247
```

**Usage:**
```python
import international_urns as iurns

validator = iurns.get_validator('es', 'dir3')
result = validator('urn:es:dir3:E00010201')
```

**Validation Rules:**
- Must be exactly **9 characters** total
- First character(s) must be a valid administration level code
- Remaining characters must be digits (8 for single-letter, 7 for double-letter prefixes)
- Based on Ley 39/2015 and National Interoperability Scheme

**Extracted Metadata:**
```python
# State Administration
metadata = iurns.extract_urn('urn:es:dir3:E00010201')
# Returns:
# {
#     'country_code': 'es',
#     'document_type': 'dir3',
#     'document_value': 'E00010201',
#     'administration_level_code': 'E',
#     'administration_level_name': 'Administración del Estado',
#     'unit_code': '00010201',
#     'is_valid_format': True
# }

# Autonomous Community (includes community info)
metadata = iurns.extract_urn('urn:es:dir3:A13000001')
# Returns:
# {
#     'administration_level_code': 'A',
#     'administration_level_name': 'Administración Autonómica',
#     'unit_code': '13000001',
#     'autonomous_community_code': '13',
#     'autonomous_community_name': 'Comunidad de Madrid',
#     'is_valid_format': True
# }

# University (includes SIIU code)
metadata = iurns.extract_urn('urn:es:dir3:U00112345')
# Returns:
# {
#     'administration_level_code': 'U',
#     'administration_level_name': 'Universidades',
#     'unit_code': '00112345',
#     'university_siiu_code': '001',
#     'is_valid_format': True
# }
```

---

### NSS (Número de la Seguridad Social)

The NSS is the Social Security Number used in Spain.

**Format:** 12 digits, optionally formatted with slashes

**Structure:**
- First 2 digits: Province code (01-52 or special codes 66-99)
- Next 8 digits: Sequential number
- Last 2 digits: Check digits (calculated using modulo 97)

**Examples:**
- `281234567840` (without slashes)
- `28/12345678/40` (with slashes)

**URN Format:**
```
urn:es:nss:281234567840
urn:es:nss:28/12345678/40
```

**Usage:**
```python
import international_urns as iurns

validator = iurns.get_validator('es', 'nss')

# Without slashes
result1 = validator('urn:es:nss:281234567840')

# With slashes
result2 = validator('urn:es:nss:28/12345678/40')
```

**Validation Rules:**
- Must be exactly 12 digits
- Province code must be 01-52 (Spanish provinces) or 66-99 (special codes)
- Check digits validated using modulo 97 algorithm
- Accepts format with or without slashes

**Extracted Metadata:**
```python
metadata = iurns.extract_urn('urn:es:nss:281234567840')
# Returns:
# {
#     'country_code': 'es',
#     'document_type': 'nss',
#     'document_value': '281234567840',
#     'province_code': '28',
#     'province_name': 'Madrid',
#     'sequential_number': '12345678',
#     'check_digits': '40',
#     'format': 'continuous',  # or 'slashes'
#     'is_special_code': False,
#     'is_valid_format': True
# }
```

---

### License Plates (Matrículas)

Spanish vehicle license plates. Supports current, historical, and special formats.

**Current Format (since 2000):** 4 digits + 3 consonants (no vowels)

**Old Format (1971-2000):** 1-2 province letters + 4 digits + 1-2 letters

**Special Formats:** Diplomatic (CD), Consular (CC), Foreign (E), etc.

**Examples:**

*Current format:*
- `1234BBC`
- `0000ZZZ`
- `9999DFG`

*Old format:*
- `M1234AB` (Madrid)
- `B5678XY` (Barcelona)
- `PM9012CD` (Palma de Mallorca)

*Special format:*
- `CD1234` (Diplomatic)
- `CC12345` (Consular)
- `E12345` (Foreign)

**URN Format:**
```
urn:es:plate:1234BBC
urn:es:plate:M1234AB
urn:es:matricula:1234BBC
```

**Usage:**
```python
import international_urns as iurns

validator = iurns.get_validator('es', 'plate')

# Current format
result1 = validator('urn:es:plate:1234BBC')

# Old format
result2 = validator('urn:es:plate:M1234AB')

# With spaces or hyphens (automatically normalized)
result3 = validator('urn:es:plate:1234 BBC')
result4 = validator('urn:es:plate:M-1234-AB')
```

**Validation Rules:**

*Current format:*
- Must be 4 digits + 3 consonants
- Allowed consonants: B, C, D, F, G, H, J, K, L, M, N, P, R, S, T, V, W, X, Y, Z
- No vowels (A, E, I, O, U), Ñ, or Q allowed

*Old format:*
- Province code must be valid (M, B, MA, PM, etc.)
- Followed by 4 digits
- Ending with 1-2 letters

*Special format:*
- Recognized prefixes: CD, CC, E, ET, CMD, DGP, MF, MMA, PMM, CNP
- Followed by 4-5 digits

**Extracted Metadata:**
```python
# Current format
metadata = iurns.extract_urn('urn:es:plate:1234BBC')
# Returns: {'plate_format': 'current', 'digits': '1234', 'letters': 'BBC', ...}

# Old format
metadata = iurns.extract_urn('urn:es:plate:M1234AB')
# Returns: {'plate_format': 'old', 'province_code': 'M',
#           'province_name': 'Madrid', 'digits': '1234', 'letters': 'AB', ...}

# Special format
metadata = iurns.extract_urn('urn:es:plate:CD1234')
# Returns: {'plate_format': 'special', 'special_type': 'CD',
#           'special_type_description': 'Cuerpo Diplomático (Diplomatic Corps)', ...}
```

---

## Pydantic Integration

All validators work seamlessly with Pydantic v2 using `AfterValidator` annotations.

### Option 1: Pre-defined Type Aliases (Recommended)

The plugin provides convenient pre-defined type aliases in the `integrations.pydantic` module:

```python
from pydantic import BaseModel
from international_urns_es.integrations.pydantic import DNI_URN, CIF_URN, PLATE_URN

class Person(BaseModel):
    name: str
    dni: DNI_URN

class Company(BaseModel):
    name: str
    cif: CIF_URN
    vehicles: list[PLATE_URN]

# Usage
person = Person(name="John Doe", dni="urn:es:dni:12345678Z")
company = Company(
    name="Example SL",
    cif="urn:es:cif:B01234566",
    vehicles=["urn:es:plate:1234BBC", "urn:es:plate:5678DFG"]
)
```

Available type aliases: `DNI_URN`, `NIE_URN`, `NIF_URN`, `CIF_URN`, `DIR3_URN`, `NSS_URN`, `PLATE_URN`, `MATRICULA_URN`

### Option 2: Using the Registry Interface

You can also create type aliases directly using the registry:

```python
from typing import Annotated

import international_urns as iurns
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator, BeforeValidator


# Create type aliases using validators directly from the registry
DNI_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "dni"))]
CIF_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "cif"))]

# Type alias with both BeforeValidator and AfterValidator
DNI_URN_NORMALIZED = Annotated[
    str,
    BeforeValidator(str.strip),  # Built-in normalization
    AfterValidator(iurns.get_validator("es", "dni")),
]


# Use in models
class Person(BaseModel):
    name: str
    dni_urn: DNI_URN


class Company(BaseModel):
    name: str
    cif_urn: CIF_URN


class Employee(BaseModel):
    name: str
    dni_urn: DNI_URN_NORMALIZED  # Strips whitespace before validation


# Usage
person = Person(name="John Doe", dni_urn="urn:es:dni:12345678Z")
company = Company(name="Example SL", cif_urn="urn:es:cif:B01234566")  # SL uses B prefix
employee = Employee(name="Jane Doe", dni_urn="  urn:es:dni:12345678Z  ")  # Auto-strips
```

### Advanced Pydantic Examples

**Multiple validators in one model:**

```python
# Define additional validators using registry
PLATE_URN = Annotated[str, AfterValidator(iurns.get_validator("es", "plate"))]

class SpanishEntity(BaseModel):
    name: str
    dni_urn: DNI_URN | None = None
    cif_urn: CIF_URN | None = None
    plate_urn: PLATE_URN | None = None

# Person with DNI and vehicle
person = SpanishEntity(
    name="John Doe",
    dni_urn="urn:es:dni:12345678Z",
    plate_urn="urn:es:plate:1234BBC"
)
```

**List validation:**

```python
class CompanyFleet(BaseModel):
    company_name: str
    cif_urn: CIF_URN
    vehicles: list[PLATE_URN]

# SL companies use B prefix
fleet = CompanyFleet(
    company_name="Transport SL",
    cif_urn="urn:es:cif:B01234566",
    vehicles=["urn:es:plate:1234BBC", "urn:es:plate:5678DFG"]
)
```

## Faker Integration

The plugin provides a Faker provider for generating random valid Spanish URN data for testing purposes.

```python
from faker import Faker
from international_urns_es.integrations.faker import SpanishURNProvider

# Create a Faker instance and add the provider
fake = Faker()
fake.add_provider(SpanishURNProvider)

# Generate random Spanish URNs
dni = fake.dni_urn()
print(dni)  # urn:es:dni:43335678K (random)

nie = fake.nie_urn()
print(nie)  # urn:es:nie:Y1234567M (random)

cif = fake.cif_urn()
print(cif)  # urn:es:cif:B12345670 (random)

plate = fake.plate_urn()
print(plate)  # urn:es:plate:5678DFG (random)
```

### Available Faker Methods

The `SpanishURNProvider` provides the following methods:

- `dni_urn()` - Generate a random DNI URN
- `nie_urn()` - Generate a random NIE URN
- `nif_urn()` - Generate a random NIF URN (DNI or NIE format)
- `cif_urn()` - Generate a random CIF URN
- `dir3_urn()` - Generate a random DIR3 URN
- `nss_urn()` - Generate a random NSS URN
- `plate_urn()` - Generate a random license plate URN
- `matricula_urn()` - Generate a random license plate URN (alternative name)

### Integration with Pydantic and Faker

Combine both integrations for powerful test data generation:

```python
from faker import Faker
from pydantic import BaseModel

from international_urns_es.integrations.faker import SpanishURNProvider
from international_urns_es.integrations.pydantic import DNI_URN, CIF_URN

# Setup Faker
fake = Faker()
fake.add_provider(SpanishURNProvider)

# Define Pydantic model
class Person(BaseModel):
    name: str
    dni: DNI_URN

class Company(BaseModel):
    name: str
    cif: CIF_URN

# Generate random valid test data
person = Person(name=fake.name(), dni=fake.dni_urn())
company = Company(name=fake.company(), cif=fake.cif_urn())

print(person)  # name='John Doe' dni='urn:es:dni:43335678K'
print(company)  # name='Example SL' cif='urn:es:cif:B12345670'
```

## Development

### Setup

```bash
# Clone the repository
git clone https://gitlab.com/Kencho1/international-urns-es.git
cd international-urns-es

# Create virtual environment with uv
uv venv

# Install dependencies with dev extras
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=international_urns_es --cov-report=html

# Run specific test file
pytest tests/test_dni.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Run ruff linter
ruff check .

# Run ruff formatter
ruff format .

# Run mypy type checker
mypy international_urns_es
```

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass
2. Code passes ruff and mypy checks
3. New validators include comprehensive tests
4. Documentation is updated

## License

MIT License

## Links

- [GitLab Repository](https://gitlab.com/Kencho1/international-urns-es)
- [Issue Tracker](https://gitlab.com/Kencho1/international-urns-es/-/issues)
- [International URNs](https://github.com/international-urns/international-urns)
- [PyPI Package](https://pypi.org/project/international-urns-es/)

## References

### Official Documentation

- [DNI - Spanish National ID](https://www.dnie.es/)
- [NIE - Foreigner ID](https://www.inclusion.gob.es/web/guest/nie)
- [Seguridad Social - Social Security](https://www.seg-social.es/)
- [DIR3 - Administrative Directory](https://administracionelectronica.gob.es/ctt/dir3)
- [DGT - Vehicle Plates](https://www.dgt.es/)

### Algorithm References

- DNI/NIE check letter calculation uses modulo 23
- CIF check digit uses weighted sum algorithm
- NSS check digits use modulo 97
- License plate formats follow Spanish regulations from different eras
