"""Contains code related to getting information about installed distributions."""
from functools import cache
from importlib import metadata

from .model import Distribution


class InstalledDistributionConverter:
    """Converts installed distribution objects into distribution objects from the model."""

    _get_installed_distributions_func = staticmethod(metadata.distributions)

    @cache
    def __call__(self) -> dict[str, Distribution]:
        """Return a dictionary containing all installed distributions."""
        conv_dists: dict[str, Distribution] = {}
        for orig_dist in self._get_installed_distributions_func():
            conv_files = set(str(f.locate()) for f in orig_dist.files) if orig_dist.files else set()
            conv_dist = Distribution(orig_dist.metadata["Name"], orig_dist.metadata["Version"], conv_files)
            conv_dists[conv_dist.name] = conv_dist
        return conv_dists

    def __repr__(self) -> str:
        """Return a string representation of the translator."""
        return f"{self.__class__.__name__}()"


get_installed_distributions = InstalledDistributionConverter()
