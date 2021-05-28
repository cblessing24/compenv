"""Contains code related to getting information about installed distributions."""
from functools import cache
from importlib import metadata

from .model import Distribution, Module


class InstalledDistributionConverter:
    """Converts installed distribution objects into distribution objects from the model."""

    _get_installed_distributions_func = staticmethod(metadata.distributions)

    @cache
    def __call__(self) -> dict[str, Distribution]:
        """Return a dictionary containing all installed distributions."""
        conv_dists: dict[str, Distribution] = {}
        for orig_dist in self._get_installed_distributions_func():
            conv_dist = self._convert_distribution(orig_dist)
            conv_dists[conv_dist.name] = conv_dist
        return conv_dists

    def _convert_distribution(self, orig_dist: metadata.Distribution) -> Distribution:
        if orig_dist.files:
            modules = self._convert_files_to_modules(set(orig_dist.files))
        else:
            modules = set()
        return Distribution(orig_dist.metadata["Name"], orig_dist.metadata["Version"], modules)

    @staticmethod
    def _convert_files_to_modules(files: set[metadata.PackagePath]) -> set[Module]:
        valid_files = {f for f in files if f.suffix == ".py"}
        abs_files = {f.locate() for f in valid_files}
        existing_files = {f for f in abs_files if f.exists()}  # type: ignore
        return {Module(f.stem, str(f)) for f in existing_files}  # type: ignore

    def __repr__(self) -> str:
        """Return a string representation of the translator."""
        return f"{self.__class__.__name__}()"


get_installed_distributions = InstalledDistributionConverter()
