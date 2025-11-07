"""Built-in validators and extractors for general URN formats."""

import re

from .base import URNExtractor, URNValidator


class WildcardValidator(URNValidator):
    """Validator for wildcard URN format: urn:--:--:...

    Accepts any URN with a 2-letter country code, document type, and value.
    Pattern: urn:[a-z]{2}:[^:]+:.+
    """

    country_code = "--"
    document_types = ["--"]

    def validate(self, urn: str) -> str:
        """Validate wildcard URN format.

        :param urn: The URN string to validate
        :type urn: str
        :return: The validated URN string
        :rtype: str
        :raises ValueError: If the URN doesn't match the basic format
        """
        if not re.match(r"^urn:([a-z]{2}|--):[^:]+:.+$", urn, re.IGNORECASE):
            raise ValueError(
                f"Invalid URN format. Expected 'urn:[country]:[type]:[value]' "
                f"where country is 2 letters or '--', but got: {urn}"
            )

        return urn


class WildcardExtractor(URNExtractor):
    """Extractor for wildcard URN format: urn:--:--:...

    Extracts basic metadata from any valid URN using urnparse.
    Returns country_code, document_type, and document_value.

    This extractor uses the default implementation from URNExtractor
    and does not add any document-specific metadata.
    """

    country_code = "--"
    document_types = ["--"]


__all__ = ["WildcardValidator", "WildcardExtractor"]
