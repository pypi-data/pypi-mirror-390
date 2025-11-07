"""Central registry for URN generators."""

import re
from typing import Protocol


class GeneratorFunc(Protocol):
    """Protocol for generator functions.

    Generators must return a randomly generated valid URN string.
    Compatible with Faker provider methods.
    """

    def __call__(self) -> str: ...


def _validate_country_code(country_code: str) -> None:
    """Validate that country code follows ISO 3166-1 Alpha-2 format.

    :param country_code: Country code to validate
    :type country_code: str
    :raises ValueError: If country code is not 2 alphabetic characters
    """
    if not re.match(r"^[a-zA-Z]{2}$", country_code):
        raise ValueError(
            f"Country code must be ISO 3166-1 Alpha-2 (2 letters). Got: {country_code}"
        )


class URNGeneratorRegistry:
    """Centralized registry for country/document-type specific URN generators.

    The registry maintains a mapping of (country_code, document_type) tuples to
    generator functions. Country codes must be ISO 3166-1 Alpha-2 codes.
    Wildcard ('--') is not supported for generators.
    """

    def __init__(self) -> None:
        self._generators: dict[tuple[str, str], GeneratorFunc] = {}

    def register(
        self,
        country_code: str,
        document_type: str,
        generator: GeneratorFunc
    ) -> None:
        """Register a generator for a specific country and document type.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :param generator: Generator function that returns a URN string
        :type generator: GeneratorFunc
        :raises ValueError: If country code is invalid or generator already registered
        """
        _validate_country_code(country_code)

        key = (country_code.lower(), document_type.lower())
        if key in self._generators:
            raise ValueError(
                f"Generator already registered for {country_code}:{document_type}"
            )
        self._generators[key] = generator

    def get_generator(self, country_code: str, document_type: str) -> GeneratorFunc | None:
        """Get a generator for a specific country and document type.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :return: The generator function, or None if not found
        :rtype: GeneratorFunc | None
        """
        key = (country_code.lower(), document_type.lower())
        return self._generators.get(key)

    def list_generators(self) -> list[tuple[str, str]]:
        """List all registered (country_code, document_type) combinations.

        :return: List of tuples containing country codes and document types
        :rtype: list[tuple[str, str]]
        """
        return list(self._generators.keys())

    def has_generator(self, country_code: str, document_type: str) -> bool:
        """Check if a generator exists for the given combination.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :return: True if a generator is registered, False otherwise
        :rtype: bool
        """
        key = (country_code.lower(), document_type.lower())
        return key in self._generators


_generator_registry = URNGeneratorRegistry()


def get_generator_registry() -> URNGeneratorRegistry:
    """Get the global URN generator registry instance.

    :return: The singleton URNGeneratorRegistry instance
    :rtype: URNGeneratorRegistry
    """
    return _generator_registry


__all__ = ["GeneratorFunc", "URNGeneratorRegistry", "get_generator_registry"]
