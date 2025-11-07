"""Central registry for URN validators."""

import re
from typing import Protocol


class ValidatorFunc(Protocol):
    """Protocol for validator functions.

    Validators must accept a URN string and return the validated/normalized URN.
    They should raise ValueError or ValidationError on invalid input.
    """

    def __call__(self, urn: str) -> str: ...


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


class URNValidatorRegistry:
    """Centralized registry for country/document-type specific URN validators.

    The registry maintains a mapping of (country_code, document_type) tuples to
    validator functions. Country codes must be ISO 3166-1 Alpha-2 codes.
    """

    def __init__(self) -> None:
        self._validators: dict[tuple[str, str], ValidatorFunc] = {}

    def register(
        self,
        country_code: str,
        document_type: str,
        validator: ValidatorFunc
    ) -> None:
        """Register a validator for a specific country and document type.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :param validator: Validator function that accepts and returns a URN string
        :type validator: ValidatorFunc
        :raises ValueError: If country code is invalid or validator already registered
        """
        _validate_country_code(country_code)

        key = (country_code.lower(), document_type.lower())
        if key in self._validators:
            raise ValueError(
                f"Validator already registered for {country_code}:{document_type}"
            )
        self._validators[key] = validator

    def get_validator(self, country_code: str, document_type: str) -> ValidatorFunc | None:
        """Get a validator for a specific country and document type.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :return: The validator function, or None if not found
        :rtype: ValidatorFunc | None
        """
        key = (country_code.lower(), document_type.lower())
        return self._validators.get(key)

    def list_validators(self) -> list[tuple[str, str]]:
        """List all registered (country_code, document_type) combinations.

        :return: List of tuples containing country codes and document types
        :rtype: list[tuple[str, str]]
        """
        return list(self._validators.keys())

    def has_validator(self, country_code: str, document_type: str) -> bool:
        """Check if a validator exists for the given combination.

        :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
        :type country_code: str
        :param document_type: Document type identifier (case-insensitive)
        :type document_type: str
        :return: True if a validator is registered, False otherwise
        :rtype: bool
        """
        key = (country_code.lower(), document_type.lower())
        return key in self._validators


_validator_registry = URNValidatorRegistry()


def get_validator_registry() -> URNValidatorRegistry:
    """Get the global URN validator registry instance.

    :return: The singleton URNValidatorRegistry instance
    :rtype: URNValidatorRegistry
    """
    return _validator_registry


__all__ = ["ValidatorFunc", "URNValidatorRegistry", "get_validator_registry"]
