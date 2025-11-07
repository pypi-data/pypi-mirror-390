"""Normalization utilities for URN strings."""

import re
from collections.abc import Callable


def normalize_urn(urn: str) -> str:
    """Normalize a URN by lowercasing case-insensitive parts.

    The URN scheme ('urn'), country code (NID), and document type (first NSS segment)
    are converted to lowercase. The remainder of the NSS is preserved as-is.

    :param urn: The URN string to normalize
    :type urn: str
    :return: Normalized URN string
    :rtype: str
    :raises ValueError: If the URN format is invalid

    Example::

        >>> normalize_urn("URN:ES:DNI:12345678X")
        "urn:es:dni:12345678X"
    """
    pattern = r"^(urn):([^:]+):([^:]+):(.+)$"
    match = re.match(pattern, urn, re.IGNORECASE)

    if not match:
        raise ValueError(f"Invalid URN format: {urn}")

    scheme, country, doc_type, remainder = match.groups()

    return f"{scheme.lower()}:{country.lower()}:{doc_type.lower()}:{remainder}"


def create_normalizer() -> Callable[[str], str]:
    """Create a normalization function suitable for use with Pydantic BeforeValidator.

    :return: A function that normalizes URN strings
    :rtype: Callable[[str], str]

    Example::

        from pydantic import BaseModel, BeforeValidator
        from typing import Annotated

        class Document(BaseModel):
            urn: Annotated[str, BeforeValidator(create_normalizer())]
    """
    return normalize_urn


__all__ = ["normalize_urn", "create_normalizer"]
