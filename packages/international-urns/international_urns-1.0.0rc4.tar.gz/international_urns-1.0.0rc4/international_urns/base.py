"""Base classes for URN validators, generators, and extractors."""

from abc import ABC, abstractmethod
from typing import Any

from .extractors_registry import get_extractor_registry
from .generators_registry import get_generator_registry
from .validators_registry import get_validator_registry


class URNValidator(ABC):
    """Base class for URN validators with automatic registration.

    Subclasses should define class attributes:
    - country_code: ISO 3166-1 Alpha-2 country code
    - document_types: List of document type identifiers

    The validator will automatically register itself for all specified
    document types when the class is defined.
    """

    country_code: str
    document_types: list[str]

    def __init_subclass__(cls, **kwargs: dict) -> None:
        """Automatically register validator when subclass is created.

        :param kwargs: Additional keyword arguments
        :type kwargs: dict
        """
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "country_code") or not hasattr(cls, "document_types"):
            return

        registry = get_validator_registry()

        for doc_type in cls.document_types:
            validator_instance = cls()
            registry.register(
                cls.country_code,
                doc_type,
                validator_instance.validate
            )

    @abstractmethod
    def validate(self, urn: str) -> str:
        """Validate and return the URN.

        :param urn: The URN string to validate
        :type urn: str
        :return: The validated/normalized URN string
        :rtype: str
        :raises ValueError: If the URN is invalid
        """
        pass


class URNGenerator(ABC):
    """Base class for URN generators with automatic registration.

    Subclasses should define class attributes:
    - country_code: ISO 3166-1 Alpha-2 country code
    - document_types: List of document type identifiers

    The generator will automatically register itself for all specified
    document types when the class is defined.
    """

    country_code: str
    document_types: list[str]

    def __init__(self, document_type: str | None = None) -> None:
        """Initialize the generator with optional document type.

        :param document_type: The document type this instance generates
        :type document_type: str | None
        """
        self.document_type = document_type

    def __init_subclass__(cls, **kwargs: dict) -> None:
        """Automatically register generator when subclass is created.

        :param kwargs: Additional keyword arguments
        :type kwargs: dict
        """
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "country_code") or not hasattr(cls, "document_types"):
            return

        registry = get_generator_registry()

        for doc_type in cls.document_types:
            generator_instance = cls(document_type=doc_type)
            registry.register(
                cls.country_code,
                doc_type,
                generator_instance.generate
            )

    @abstractmethod
    def generate(self) -> str:
        """Generate and return a random valid URN.

        :return: A randomly generated URN string
        :rtype: str
        """
        pass


class URNExtractor(ABC):
    """Base class for URN metadata extractors with automatic registration.

    Subclasses should define class attributes:
    - country_code: ISO 3166-1 Alpha-2 country code
    - document_types: List of document type identifiers

    The extractor will automatically register itself for all specified
    document types when the class is defined.

    This class uses the template method pattern: the extract() method
    handles basic URN parsing and calls _extract_metadata() for
    document-specific extraction.
    """

    country_code: str
    document_types: list[str]

    def __init__(self, document_type: str | None = None) -> None:
        """Initialize the extractor with optional document type.

        :param document_type: The document type this instance extracts
        :type document_type: str | None
        """
        self.document_type = document_type

    def __init_subclass__(cls, **kwargs: dict) -> None:
        """Automatically register extractor when subclass is created.

        :param kwargs: Additional keyword arguments
        :type kwargs: dict
        """
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "country_code") or not hasattr(cls, "document_types"):
            return

        registry = get_extractor_registry()

        for doc_type in cls.document_types:
            extractor_instance = cls(document_type=doc_type)
            registry.register(
                cls.country_code,
                doc_type,
                extractor_instance.extract
            )

    def extract(self, urn: str) -> dict[str, Any]:
        """Extract metadata from a URN.

        This method parses the URN to extract basic fields (country_code,
        document_type, document_value) and then calls _extract_metadata()
        to get document-specific fields.

        :param urn: The URN string to extract metadata from
        :type urn: str
        :return: Dictionary containing extracted metadata with at minimum
                 country_code, document_type, and document_value
        :rtype: dict[str, Any]
        :raises ValueError: If the URN is invalid
        """
        from urnparse import URN8141, InvalidURNFormatError

        # Normalize the URN scheme to lowercase for urnparse compatibility
        # URN scheme is case-insensitive per RFC 8141
        # Only normalize the scheme prefix, preserve case elsewhere
        if urn.upper().startswith("URN:"):
            normalized_urn = "urn" + urn[3:]
        else:
            normalized_urn = urn

        try:
            # Parse the URN to extract basic components
            parsed = URN8141.from_string(normalized_urn)
        except (InvalidURNFormatError, Exception) as e:
            raise ValueError(f"Invalid URN format: {urn}") from e

        # Use urnparse's tokenization to extract document_type and document_value from NSS
        # The parts property contains the NSS already split by colons
        nss_parts = parsed.specific_string.parts
        if len(nss_parts) < 2:
            raise ValueError(
                f"Invalid URN NSS format. Expected 'type:value' but got: {parsed.specific_string}"
            )

        document_type = nss_parts[0].lower()
        # Rejoin remaining parts with colons to handle values containing colons
        document_value = ":".join(nss_parts[1:])

        country_code = str(parsed.namespace_id).lower()

        # Build base result
        result = {
            "country_code": country_code,
            "document_type": document_type,
            "document_value": document_value,
        }

        # Add document-specific metadata
        specific_metadata = self._extract_metadata(
            country_code=country_code,
            document_type=document_type,
            document_value=document_value,
            nss_parts=nss_parts
        )
        result.update(specific_metadata)

        return result

    def _extract_metadata(
        self,
        country_code: str,
        document_type: str,
        document_value: str,
        nss_parts: list[str]
    ) -> dict[str, Any]:
        """Extract document-specific metadata from the URN.

        Subclasses can override this method to add additional metadata
        fields beyond the basic country_code, document_type, and
        document_value.

        :param country_code: The country code (NID) extracted from the URN
        :type country_code: str
        :param document_type: The document type extracted from the NSS
        :type document_type: str
        :param document_value: The document value portion (remainder of NSS)
        :type document_value: str
        :param nss_parts: The tokenized NSS parts from urnparse
        :type nss_parts: list[str]
        :return: Dictionary containing additional metadata fields
        :rtype: dict[str, Any]
        """
        return {}


__all__ = ["URNValidator", "URNGenerator", "URNExtractor"]
