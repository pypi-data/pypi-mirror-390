"""Validator factory functions."""

from .validators_registry import ValidatorFunc, get_validator_registry


def get_validator(country_code: str, document_type: str) -> ValidatorFunc:
    """Get a validator function for a specific country and document type.

    This function is intended for use with Pydantic's AfterValidator.

    :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
    :type country_code: str
    :param document_type: Document type identifier (case-insensitive)
    :type document_type: str
    :return: A validator function that accepts and returns a URN string
    :rtype: ValidatorFunc
    :raises ValueError: If no validator is registered for the combination

    Example::

        from pydantic import BaseModel, AfterValidator
        from typing import Annotated
        import international_urns as iurns

        class Document(BaseModel):
            dni: Annotated[str, AfterValidator(
                iurns.get_validator('es', 'dni')
            )]
    """
    registry = get_validator_registry()
    validator = registry.get_validator(country_code, document_type)

    if validator is None:
        raise ValueError(
            f"No validator registered for {country_code}:{document_type}. "
            f"Available validators: {registry.list_validators()}"
        )

    return validator


def list_validators() -> list[tuple[str, str]]:
    """List all registered (country_code, document_type) combinations.

    :return: List of tuples containing country codes and document types
    :rtype: list[tuple[str, str]]

    Example::

        >>> import international_urns as iurns
        >>> iurns.list_validators()
        [('--', '--'), ('es', 'dni'), ('es', 'nie')]
    """
    registry = get_validator_registry()
    return registry.list_validators()


def has_validator(country_code: str, document_type: str) -> bool:
    """Check if a validator exists for the given combination.

    :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
    :type country_code: str
    :param document_type: Document type identifier (case-insensitive)
    :type document_type: str
    :return: True if a validator is registered, False otherwise
    :rtype: bool

    Example::

        >>> import international_urns as iurns
        >>> iurns.has_validator('es', 'dni')
        True
        >>> iurns.has_validator('fr', 'nie')
        False
    """
    registry = get_validator_registry()
    return registry.has_validator(country_code, document_type)


__all__ = ["get_validator", "list_validators", "has_validator"]
