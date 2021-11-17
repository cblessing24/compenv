"""Contains code related to getting information about installed distributions."""
from functools import lru_cache
from importlib import metadata
from pathlib import Path
from typing import Set

from ..model.record import Distribution, InstalledDistributions, Module, Modules
from .module import ActiveModuleConverter


class InstalledDistributionConverter:
    """Converts installed distribution objects into distribution objects from the model."""

    _get_installed_distributions_func = staticmethod(metadata.distributions)
    _path_cls = Path
    _get_active_modules_func = ActiveModuleConverter()

    @lru_cache(maxsize=None)
    def __call__(self) -> InstalledDistributions:
        """Return a dictionary containing all installed distributions."""
        conv_dists: Set[Distribution] = set()
        for orig_dist in self._get_installed_distributions_func():
            conv_dists.add(self._convert_distribution(orig_dist))
        return InstalledDistributions(conv_dists)

    def _convert_distribution(self, orig_dist: metadata.Distribution) -> Distribution:
        if orig_dist.files:
            modules = self._convert_files_to_modules(set(orig_dist.files))
        else:
            modules = set()
        return Distribution(orig_dist.metadata["Name"], orig_dist.metadata["Version"], modules=Modules(modules))

    def _convert_files_to_modules(self, files: Set[metadata.PackagePath]) -> Set[Module]:
        valid_files = {f for f in files if f.suffix == ".py"}
        abs_files = {self._path_cls(f.locate()) for f in valid_files}
        existing_files = {f for f in abs_files if f.exists()}
        active_files = {m.file for m in self._get_active_modules_func()}
        return {Module(f, is_active=f in active_files) for f in existing_files}

    def __repr__(self) -> str:
        """Return a string representation of the translator."""
        return f"{self.__class__.__name__}()"
