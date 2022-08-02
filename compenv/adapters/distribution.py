"""Contains code related to getting information about installed distributions."""
from __future__ import annotations

from functools import lru_cache
from importlib import metadata
from os import PathLike
from pathlib import Path
from typing import Callable, Iterable, Literal, Optional, Protocol, Set, Type

from ..model.record import ActiveModules, Distribution, InstalledDistributions, Module, Modules
from .module import ActiveModuleConverter


class _ExistenceCheckablePath(Protocol):
    """Path-like object that supports checking for its existence."""

    def __init__(self, path: PathLike[str]) -> None:
        """Initialize the path."""

    def exists(self) -> bool:
        """Return True if the path exists, false otherwise."""

    def __fspath__(self) -> str:
        """Return the file system representation of the path."""


class _PackagePath(Protocol):
    """Interface of a distribution's package paths expected by the converter."""

    @property
    def suffix(self) -> str:
        """Return the extension of the path."""

    def locate(self) -> PathLike[str]:
        """Locate the path in the file system."""


class _Metadata(Protocol):  # pylint: disable=too-few-public-methods
    """Interface of distribution metadata expected by the converter."""

    def __getitem__(self, item: Literal["Name", "Version"]) -> str:
        """Get the value corresponding to the provided item."""


class _MetadataDistribution(Protocol):
    """Interface of distributions expected by the converter."""

    @property
    def files(self) -> Optional[Iterable[_PackagePath]]:
        """Return the paths of the files associated with the distribution."""

    @property
    def metadata(self) -> _Metadata:
        """Return the distribution's metadata."""


class InstalledDistributionConverter:
    """Converts installed distribution objects into distribution objects from the model."""

    def __init__(
        self,
        path_cls: Type[_ExistenceCheckablePath] = Path,
        get_installed_distributions: Callable[[], Iterable[_MetadataDistribution]] = metadata.distributions,
        get_active_modules: Optional[Callable[[], ActiveModules]] = None,
    ) -> None:
        """Initialize the installed distribution converter."""
        if get_active_modules is None:
            get_active_modules = ActiveModuleConverter()
        self._path_cls = path_cls
        self._get_installed_distributions = get_installed_distributions
        self._get_active_modules = get_active_modules

    @lru_cache
    def __call__(self) -> InstalledDistributions:
        """Return a dictionary containing all installed distributions."""
        conv_dists: Set[Distribution] = set()
        for orig_dist in self._get_installed_distributions():
            conv_dists.add(self._convert_distribution(orig_dist))
        return InstalledDistributions(conv_dists)

    def _convert_distribution(self, orig_dist: _MetadataDistribution) -> Distribution:
        if orig_dist.files:
            modules = self._convert_files_to_modules(set(orig_dist.files))
        else:
            modules = set()
        return Distribution(orig_dist.metadata["Name"], orig_dist.metadata["Version"], modules=Modules(modules))

    def _convert_files_to_modules(self, files: Set[_PackagePath]) -> Set[Module]:
        valid_files = {f for f in files if f.suffix == ".py"}
        abs_files = {self._path_cls(f.locate()) for f in valid_files}
        existing_files = {f for f in abs_files if f.exists()}
        active_files = {m.file for m in self._get_active_modules()}
        return {Module(f, is_active=f in active_files) for f in existing_files}

    def __repr__(self) -> str:
        """Return a string representation of the translator."""
        return f"{self.__class__.__name__}()"
