"""Central registry for URN metadata extractors."""

import re
from typing import Any, Protocol


class ExtractorFunc(Protocol):
    """Protocol for extractor functions.

    Extractors must accept a URN string and return a dictionary with metadata.
    """

    def __call__(self, urn: str) -> dict[str, Any]: ...


def _validate_country_code(country_code: str) -> None:
    """Validate that country code follows ISO 3166-1 Alpha-2 format.

    :param country_code: Country code to validate
    :type country_code: str
    :raises ValueError: If country code is not 2 alphabetic characters or "--"
    """
    if not re.match(r"^([a-zA-Z]{2}|--)$", country_code):
        raise ValueError(
            f"Country code must be ISO 3166-1 Alpha-2 (2 letters) or '--'. Got: {country_code}"
        )


class URNExtractorRegistry:
    """Centralized registry for country/document-type specific URN metadata extractors.

    The registry maintains a mapping of (country_code, document_type) tuples to
    extractor functions. Country codes must be ISO 3166-1 Alpha-2 codes.
    """

    def __init__(self) -> None:
        self._extractors: dict[tuple[str, str], ExtractorFunc] = {}

    def register(
        self,
        country_code: str,
        document_type: str,
        extractor: ExtractorFunc
    ) -> None:
        """Register an extractor for a specific country and document type.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :param extractor: Extractor function that accepts a URN and returns metadata dict
        :type extractor: ExtractorFunc
        :raises ValueError: If country code is invalid or extractor already registered
        """
        _validate_country_code(country_code)

        key = (country_code.lower(), document_type.lower())
        if key in self._extractors:
            raise ValueError(
                f"Extractor already registered for {country_code}:{document_type}"
            )
        self._extractors[key] = extractor

    def get_extractor(self, country_code: str, document_type: str) -> ExtractorFunc | None:
        """Get an extractor for a specific country and document type.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :return: The extractor function, or None if not found
        :rtype: ExtractorFunc | None
        """
        key = (country_code.lower(), document_type.lower())
        return self._extractors.get(key)

    def list_extractors(self) -> list[tuple[str, str]]:
        """List all registered (country_code, document_type) combinations.

        :return: List of tuples containing country codes and document types
        :rtype: list[tuple[str, str]]
        """
        return list(self._extractors.keys())

    def has_extractor(self, country_code: str, document_type: str) -> bool:
        """Check if an extractor exists for the given combination.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :return: True if an extractor is registered, False otherwise
        :rtype: bool
        """
        key = (country_code.lower(), document_type.lower())
        return key in self._extractors


_extractor_registry = URNExtractorRegistry()


def get_extractor_registry() -> URNExtractorRegistry:
    """Get the global URN extractor registry instance.

    :return: The singleton URNExtractorRegistry instance
    :rtype: URNExtractorRegistry
    """
    return _extractor_registry


__all__ = ["ExtractorFunc", "URNExtractorRegistry", "get_extractor_registry"]
