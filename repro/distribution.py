"""Contains code related to getting information about installed distributions."""
from functools import cache
from importlib import metadata
from pathlib import Path

from .model import Distribution, Module


class InstalledDistributionConverter:
    """Converts installed distribution objects into distribution objects from the model."""

    _get_installed_distributions_func = staticmethod(metadata.distributions)
    _path_cls = Path

    @cache
    def __call__(self) -> frozenset[Distribution]:
        """Return a dictionary containing all installed distributions."""
        conv_dists: set[Distribution] = set()
        for orig_dist in self._get_installed_distributions_func():
            conv_dists.add(self._convert_distribution(orig_dist))
        return frozenset(conv_dists)

    def _convert_distribution(self, orig_dist: metadata.Distribution) -> Distribution:
        if orig_dist.files:
            modules = self._convert_files_to_modules(set(orig_dist.files))
        else:
            modules = set()
        return Distribution(orig_dist.metadata["Name"], orig_dist.metadata["Version"], modules=frozenset(modules))

    def _convert_files_to_modules(self, files: set[metadata.PackagePath]) -> set[Module]:
        valid_files = {f for f in files if f.suffix == ".py"}
        abs_files = {self._path_cls(f.locate()) for f in valid_files}
        existing_files = {f for f in abs_files if f.exists()}
        return {Module(f) for f in existing_files}

    def __repr__(self) -> str:
        """Return a string representation of the translator."""
        return f"{self.__class__.__name__}()"
