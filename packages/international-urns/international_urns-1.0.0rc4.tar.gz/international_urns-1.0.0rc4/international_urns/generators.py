"""Generator factory functions."""

from .generators_registry import GeneratorFunc, get_generator_registry


def get_generator(country_code: str, document_type: str) -> GeneratorFunc:
    """Get a generator function for a specific country and document type.

    This function is intended for use with Faker providers and direct invocation.

    :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
    :type country_code: str
    :param document_type: Document type identifier (case-insensitive)
    :type document_type: str
    :return: A generator function that returns a random URN string
    :rtype: GeneratorFunc
    :raises ValueError: If no generator is registered for the combination

    Example::

        import international_urns as iurns

        # Get a generator function
        dni_gen = iurns.get_generator('es', 'dni')

        # Generate a random URN
        urn = dni_gen()
        print(urn)  # e.g., urn:es:dni:12345678Z

        # Use with Faker
        from faker import Faker
        fake = Faker()
        fake.add_provider(lambda self: setattr(self, 'es_dni', dni_gen))
        urn = fake.es_dni()
    """
    registry = get_generator_registry()
    generator = registry.get_generator(country_code, document_type)

    if generator is None:
        raise ValueError(
            f"No generator registered for {country_code}:{document_type}. "
            f"Available generators: {registry.list_generators()}"
        )

    return generator


def list_generators() -> list[tuple[str, str]]:
    """List all registered (country_code, document_type) combinations.

    :return: List of tuples containing country codes and document types
    :rtype: list[tuple[str, str]]

    Example::

        >>> import international_urns as iurns
        >>> iurns.list_generators()
        [('es', 'dni'), ('es', 'nie')]
    """
    registry = get_generator_registry()
    return registry.list_generators()


def has_generator(country_code: str, document_type: str) -> bool:
    """Check if a generator exists for the given combination.

    :param country_code: ISO 3166-1 Alpha-2 country code (case-insensitive)
    :type country_code: str
    :param document_type: Document type identifier (case-insensitive)
    :type document_type: str
    :return: True if a generator is registered, False otherwise
    :rtype: bool

    Example::

        >>> import international_urns as iurns
        >>> iurns.has_generator('es', 'dni')
        True
        >>> iurns.has_generator('fr', 'nie')
        False
    """
    registry = get_generator_registry()
    return registry.has_generator(country_code, document_type)


__all__ = ["get_generator", "list_generators", "has_generator"]
