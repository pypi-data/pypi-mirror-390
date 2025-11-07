# International URNs

A microkernel-based Python library for validating, generating, and extracting metadata from country-specific URN (Uniform Resource Name) formats.

## Overview

International URNs provides a pluggable architecture for validating, generating, and extracting metadata from URNs associated with countries using ISO 3166-1 Alpha-2 codes. The library uses a microkernel design where country-specific validators, generators, and extractors are provided by separate plugin packages.

**URN Format:** `urn:country_code:document_type:document_value`

**Example:** `urn:es:dni:12345678X`

## Features

- **Microkernel Architecture**: Core library provides the framework, plugins provide country-specific validation, generation, and extraction
- **Auto-registration**: Validators, generators, and extractors automatically register themselves using Python's `__init_subclass__`
- **Entry Point Discovery**: Plugins are discovered and loaded via Python entry points
- **ISO 3166-1 Alpha-2 Enforcement**: Country codes are validated to be exactly 2 letters (or "--" for wildcard)
- **URN Generation**: Generate random valid URNs for testing and fixtures
- **Metadata Extraction**: Extract structured metadata from URNs with automatic parser selection
- **Faker Integration**: Generators are compatible with Faker providers for easy test data generation
- **Pydantic Integration**: Seamless integration with Pydantic's `BeforeValidator` and `AfterValidator`
- **Case-Insensitive**: URN scheme, country codes, and document types are case-insensitive (NSS remainder preserves case)
- **Type-Safe**: Full type hints with mypy support
- **Extensible**: Easy to add new country and document type validators, generators, and extractors

## Installation

```bash
pip install international-urns
```

For development:

```bash
# Create virtual environment and install with test dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[test]"
```

## Usage

> **Note:** Examples use `iurns` as an abbreviated import alias for convenience.

### Basic Validation with Pydantic

```python
from pydantic import BaseModel, AfterValidator, BeforeValidator
from typing import Annotated
import international_urns as iurns

class Document(BaseModel):
    urn: Annotated[
        str,
        BeforeValidator(iurns.create_normalizer()),
        AfterValidator(iurns.get_validator('es', 'dni'))
    ]

# Validates and normalizes the URN
doc = Document(urn="URN:ES:DNI:12345678X")
print(doc.urn)  # Output: "urn:es:dni:12345678X"
```

### Normalization

URN normalization converts the scheme, country code, and document type to lowercase while preserving the case of the document value:

```python
import international_urns as iurns

normalized = iurns.normalize_urn("URN:ES:DNI:12345678X")
print(normalized)  # Output: "urn:es:dni:12345678X"
```

### Wildcard Validator

The library includes a built-in wildcard validator that accepts any URN with a 2-letter country code:

```python
import international_urns as iurns

validator = iurns.get_validator('--', '--')
result = validator('urn:es:dni:12345678X')  # Valid
result = validator('urn:us:ssn:123-45-6789')  # Valid
result = validator('urn:--:--:anything')  # Also valid
```

### Registry Introspection

```python
import international_urns as iurns

# List all available validators
validators = iurns.list_validators()
print(validators)  # [('--', '--'), ('es', 'dni'), ...]

# Check if a validator exists
if iurns.has_validator('es', 'dni'):
    validator = iurns.get_validator('es', 'dni')
    result = validator('urn:es:dni:12345678X')
```

## URN Generation

The library provides generators for creating random valid URNs, useful for testing and fixtures.

### Basic Generation

```python
import international_urns as iurns

# Get a generator for a specific country and document type
dni_generator = iurns.get_generator('es', 'dni')

# Generate a random URN
urn = dni_generator()
print(urn)  # Output: "urn:es:dni:12345678Z" (random valid DNI)
```

### Generator Registry Introspection

```python
import international_urns as iurns

# List all available generators
generators = iurns.list_generators()
print(generators)  # [('es', 'dni'), ('es', 'nie'), ...]

# Check if a generator exists
if iurns.has_generator('es', 'dni'):
    gen = iurns.get_generator('es', 'dni')
    urn = gen()
```

### Faker Integration

Generators are designed to be compatible with [Faker](https://faker.readthedocs.io/) providers:

```python
from faker import Faker
from faker.providers import BaseProvider
import international_urns as iurns

class SpanishURNProvider(BaseProvider):
    def spanish_dni(self):
        return iurns.get_generator('es', 'dni')()

    def spanish_nie(self):
        return iurns.get_generator('es', 'nie')()

fake = Faker()
fake.add_provider(SpanishURNProvider)

# Generate random URNs
dni = fake.spanish_dni()
nie = fake.spanish_nie()
```

## URN Metadata Extraction

The library provides extractors for parsing URNs and extracting structured metadata.

### Convenience Method

The simplest way to extract metadata is using the `extract_urn()` convenience function, which automatically selects the appropriate extractor:

```python
import international_urns as iurns

# Extract metadata from any URN
metadata = iurns.extract_urn('urn:es:dni:12345678X')

print(metadata['country_code'])    # Output: 'es'
print(metadata['document_type'])   # Output: 'dni'
print(metadata['document_value'])  # Output: '12345678X'
```

The `extract_urn()` function:
- Automatically parses the URN to determine country and document type
- Uses a specific extractor if one is registered for that country/type combination
- Falls back to the wildcard extractor if no specific extractor is available
- Returns a dictionary with at minimum: `country_code`, `document_type`, and `document_value`

### Using Specific Extractors

You can also get extractors directly from the registry:

```python
import international_urns as iurns

# Get the wildcard extractor
extractor = iurns.get_extractor('--', '--')
metadata = extractor('urn:fr:passport:ABC123')

print(metadata)
# Output: {'country_code': 'fr', 'document_type': 'passport', 'document_value': 'ABC123'}
```

### Extractor Registry Introspection

```python
import international_urns as iurns

# List all available extractors
extractors = iurns.list_extractors()
print(extractors)  # [('--', '--'), ('es', 'dni'), ...]

# Check if an extractor exists
if iurns.has_extractor('es', 'dni'):
    extractor = iurns.get_extractor('es', 'dni')
    metadata = extractor('urn:es:dni:12345678X')
```

### Custom Extractors with Additional Metadata

Plugins can provide extractors that return additional metadata fields specific to the document type. The base `URNExtractor` class uses the template method pattern: it handles extracting basic fields (country_code, document_type, document_value) automatically, and calls `_extract_metadata()` for document-specific extraction:

```python
# Example custom extractor (in a plugin)
from international_urns import URNExtractor
import re

class SpanishDNIExtractor(URNExtractor):
    country_code = "es"
    document_types = ["dni"]

    def _extract_metadata(self, country_code: str, document_type: str,
                         document_value: str, nss_parts: list[str]) -> dict:
        """Extract DNI-specific metadata.

        The base class already provides country_code, document_type, and
        document_value. This method adds document-specific fields.

        :param country_code: The country code (e.g., 'es')
        :param document_type: The document type (e.g., 'dni')
        :param document_value: The document value (e.g., '12345678X')
        :param nss_parts: Tokenized NSS parts from urnparse
        :return: Dictionary with additional metadata fields
        """
        # Extract number and letter from DNI format
        match = re.match(r'^(\d{8})([A-Z])$', document_value.upper())

        if match:
            return {
                "number": match.group(1),
                "letter": match.group(2),
            }

        return {}

# Using the custom extractor
metadata = iurns.extract_urn('urn:es:dni:12345678X')
print(metadata['country_code'])  # Output: 'es' (from base class)
print(metadata['document_type'])  # Output: 'dni' (from base class)
print(metadata['document_value'])  # Output: '12345678X' (from base class)
print(metadata['number'])  # Output: '12345678' (from _extract_metadata)
print(metadata['letter'])  # Output: 'X' (from _extract_metadata)
```

## Creating Plugins

To create a plugin for a new country or document type:

### 1. Create a new package

Example: `international-urns-es` for Spanish documents

### 2. Define validators

Subclass `URNValidator` and specify the country code (ISO 3166-1 Alpha-2) and document types:

```python
from international_urns import URNValidator

class SpanishDNIValidator(URNValidator):
    country_code = "es"  # Must be 2 letters (or "--" for wildcard)
    document_types = ["dni", "nie"]

    def validate(self, urn: str) -> str:
        # Implement validation logic
        # Raise ValueError if invalid
        # Return the URN (possibly normalized) if valid

        if not self._check_dni_format(urn):
            raise ValueError(f"Invalid DNI format: {urn}")

        return urn

    def _check_dni_format(self, urn: str) -> bool:
        # Custom validation logic here
        return True
```

### 3. Define generators

Subclass `URNGenerator` to create random URNs. Note that wildcard ("--") is not supported for generators:

```python
from international_urns import URNGenerator
import random
import string

class SpanishDNIGenerator(URNGenerator):
    country_code = "es"  # Must be 2 letters (no wildcard for generators)
    document_types = ["dni", "nie"]

    def generate(self) -> str:
        # Generate a random valid URN
        # self.document_type contains the specific document type for this instance

        # Generate random DNI number (8 digits + letter)
        number = random.randint(10000000, 99999999)
        letter = random.choice(string.ascii_uppercase)

        return f"urn:{self.country_code}:{self.document_type}:{number}{letter}"
```

**Important**: When a generator class supports multiple document types, each registration creates a separate instance with `self.document_type` set to the appropriate value. Use `self.document_type` in your `generate()` method to create the correct URN format.

### 4. Define extractors

Subclass `URNExtractor` to parse URNs and extract structured metadata. The base class uses the template method pattern and automatically extracts the basic fields (country_code, document_type, document_value). Override `_extract_metadata()` to add document-specific fields:

```python
from international_urns import URNExtractor
import re

class SpanishDNIExtractor(URNExtractor):
    country_code = "es"  # Can be 2 letters or "--" for wildcard
    document_types = ["dni", "nie"]

    def _extract_metadata(self, country_code: str, document_type: str,
                         document_value: str, nss_parts: list[str]) -> dict:
        """Extract Spanish document-specific metadata.

        The base class already provides country_code, document_type, and
        document_value. This method adds additional fields specific to
        Spanish identity documents.

        :param country_code: The country code (e.g., 'es')
        :param document_type: The document type (e.g., 'dni', 'nie')
        :param document_value: The document value extracted by base class
        :param nss_parts: Tokenized NSS parts from urnparse
        :return: Dictionary with additional metadata fields
        """
        # Extract number and letter from DNI/NIE format
        match = re.match(r'^(\d{8})([A-Z])$', document_value.upper())

        if match:
            return {
                "number": match.group(1),
                "letter": match.group(2),
            }

        return {}
```

**Important**: When an extractor class supports multiple document types, each registration creates a separate instance with `self.document_type` set to the appropriate value (though you typically won't need to use it since the base class handles document_type extraction). The base `extract()` method automatically provides `country_code`, `document_type`, and `document_value` - you only need to implement `_extract_metadata()` to add additional fields.

### 5. Register via entry points

In your plugin's `pyproject.toml`:

```toml
[project.entry-points.'international_urns.plugins']
es = 'international_urns_es'
```

Validators, generators, and extractors will automatically register themselves when the plugin is imported.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=international_urns --cov-report=html

# Run specific test file
pytest tests/test_registry.py
```

### Linting and Type Checking

```bash
# Lint and format
ruff check .
ruff format .

# Type checking
mypy international_urns
```

## Requirements

- Python 3.11+
- urnparse

## License

MIT License - see LICENSE file for details
