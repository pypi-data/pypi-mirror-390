"""Extractor factory functions."""

from typing import Any

from urnparse import URN8141

from .extractors_registry import ExtractorFunc, get_extractor_registry


def get_extractor(country_code: str, document_type: str) -> ExtractorFunc:
    """Get an extractor function for a specific country and document type.

    :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
    :type country_code: str
    :param document_type: Document type identifier (case-insensitive)
    :type document_type: str
    :return: An extractor function that accepts a URN and returns metadata dict
    :rtype: ExtractorFunc
    :raises ValueError: If no extractor is registered for the combination

    Example::

        >>> import international_urns as iurns
        >>> extractor = iurns.get_extractor('es', 'dni')
        >>> metadata = extractor('urn:es:dni:12345678X')
        >>> metadata['country_code']
        'es'
        >>> metadata['document_type']
        'dni'
    """
    registry = get_extractor_registry()
    extractor = registry.get_extractor(country_code, document_type)

    if extractor is None:
        raise ValueError(
            f"No extractor registered for {country_code}:{document_type}. "
            f"Available extractors: {registry.list_extractors()}"
        )

    return extractor


def list_extractors() -> list[tuple[str, str]]:
    """List all registered (country_code, document_type) combinations.

    :return: List of tuples containing country codes and document types
    :rtype: list[tuple[str, str]]

    Example::

        >>> import international_urns as iurns
        >>> iurns.list_extractors()
        [('--', '--'), ('es', 'dni'), ('es', 'nie')]
    """
    registry = get_extractor_registry()
    return registry.list_extractors()


def has_extractor(country_code: str, document_type: str) -> bool:
    """Check if an extractor exists for the given combination.

    :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
    :type country_code: str
    :param document_type: Document type identifier (case-insensitive)
    :type document_type: str
    :return: True if an extractor is registered, False otherwise
    :rtype: bool

    Example::

        >>> import international_urns as iurns
        >>> iurns.has_extractor('es', 'dni')
        True
        >>> iurns.has_extractor('fr', 'nie')
        False
    """
    registry = get_extractor_registry()
    return registry.has_extractor(country_code, document_type)


def extract_urn(urn: str) -> dict[str, Any]:
    """Extract metadata from a URN using the appropriate registered extractor.

    This convenience function automatically determines the country code and document
    type from the URN, looks up the appropriate extractor, and returns the extracted
    metadata. If no specific extractor is registered, falls back to the wildcard
    extractor.

    :param urn: The URN string to extract metadata from
    :type urn: str
    :return: Dictionary containing extracted metadata
    :rtype: dict[str, Any]
    :raises ValueError: If the URN format is invalid

    Example::

        >>> import international_urns as iurns
        >>> metadata = iurns.extract_urn('urn:es:dni:12345678X')
        >>> metadata['country_code']
        'es'
        >>> metadata['document_type']
        'dni'
        >>> metadata['document_value']
        '12345678X'
    """
    # Normalize the URN scheme to lowercase for urnparse compatibility
    if urn.upper().startswith("URN:"):
        normalized_urn = "urn" + urn[3:]
    else:
        normalized_urn = urn

    # Parse the URN to extract country code and document type
    try:
        parsed = URN8141.from_string(normalized_urn)
    except Exception as e:
        raise ValueError(f"Invalid URN format: {urn}") from e

    country_code = str(parsed.namespace_id).lower()
    nss_string = str(parsed.specific_string)
    nss_parts = nss_string.split(":", 1)

    if len(nss_parts) < 2:
        raise ValueError(
            f"Invalid URN NSS format. Expected 'type:value' but got: {nss_string}"
        )

    document_type = nss_parts[0].lower()

    # Try to get a specific extractor for this country/type combination
    registry = get_extractor_registry()
    extractor = registry.get_extractor(country_code, document_type)

    # Fall back to wildcard extractor if no specific extractor is found
    if extractor is None:
        extractor = registry.get_extractor("--", "--")
        if extractor is None:
            raise ValueError(
                "No extractor available. Wildcard extractor not registered."
            )

    return extractor(urn)


__all__ = ["get_extractor", "list_extractors", "has_extractor", "extract_urn"]
