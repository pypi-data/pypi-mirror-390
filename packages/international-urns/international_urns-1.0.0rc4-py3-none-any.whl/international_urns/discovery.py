"""Plugin discovery system using entry points."""

import warnings
from importlib.metadata import entry_points


def load_plugins() -> None:
    """Load all registered URN validator plugins.

    Plugins should register themselves using the 'international_urns.plugins'
    entry point group in their pyproject.toml::

        [project.entry-points.'international_urns.plugins']
        es = 'international_urns_es'

    When the plugin module is imported, validators should self-register
    using the URNValidator base class and __init_subclass__.
    """
    plugin_entries = entry_points(group="international_urns.plugins")

    for entry_point in plugin_entries:
        try:
            entry_point.load()
        except Exception as e:
            warnings.warn(
                f"Failed to load plugin '{entry_point.name}': {e}",
                RuntimeWarning,
                stacklevel=2
            )


__all__ = ["load_plugins"]
