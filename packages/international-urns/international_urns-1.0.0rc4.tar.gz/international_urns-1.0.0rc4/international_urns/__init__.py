"""International URNs - A microkernel library for country-specific URN validation.

This library provides a pluggable architecture for validating URNs associated with
countries using ISO 3166-1 Alpha-2 codes. URNs follow the format:

    urn:country_code:document_type:document_value

Example:
    urn:es:dni:12345678X
"""

__version__ = "1.0.0rc4"

# Import built-in validators and extractors to register them
# Public API
from .base import URNExtractor, URNGenerator, URNValidator
from .builtin import WildcardExtractor, WildcardValidator  # noqa: F401

# Load external plugins
from .discovery import load_plugins
from .extractors import extract_urn, get_extractor, has_extractor, list_extractors
from .extractors_registry import URNExtractorRegistry, get_extractor_registry
from .generators import get_generator, has_generator, list_generators
from .generators_registry import URNGeneratorRegistry, get_generator_registry
from .normalization import create_normalizer, normalize_urn
from .validators import get_validator, has_validator, list_validators
from .validators_registry import URNValidatorRegistry, get_validator_registry

__all__ = [
    # Version
    "__version__",
    # Validator API
    "get_validator",
    "list_validators",
    "has_validator",
    # Generator API
    "get_generator",
    "list_generators",
    "has_generator",
    # Extractor API
    "get_extractor",
    "list_extractors",
    "has_extractor",
    "extract_urn",
    # Normalization
    "normalize_urn",
    "create_normalizer",
    # Base classes for plugin development
    "URNValidator",
    "URNGenerator",
    "URNExtractor",
    # Registry access
    "URNValidatorRegistry",
    "get_validator_registry",
    "URNGeneratorRegistry",
    "get_generator_registry",
    "URNExtractorRegistry",
    "get_extractor_registry",
]

# Auto-load plugins on import
load_plugins()
