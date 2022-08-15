"""Contains code related to getting information about installed distributions."""
from __future__ import annotations

from functools import lru_cache
from importlib import metadata
from os import PathLike
from pathlib import Path
from typing import Callable, Iterable, Literal, Optional, Protocol, Set, Type

from ..model.record import Distribution, Distributions


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


class DistributionConverter:
    """Converts distribution objects into distribution objects from the model."""

    def __init__(
        self,
        path_cls: Type[_ExistenceCheckablePath] = Path,
        get_distributions: Callable[[], Iterable[_MetadataDistribution]] = metadata.distributions,
    ) -> None:
        """Initialize the distribution converter."""
        self._path_cls = path_cls
        self._get_distributions = get_distributions

    @lru_cache
    def __call__(self) -> Distributions:
        """Return a dictionary containing all distributions."""
        conv_dists: Set[Distribution] = set()
        for orig_dist in self._get_distributions():
            conv_dists.add(self._convert_distribution(orig_dist))
        return Distributions(conv_dists)

    def _convert_distribution(self, orig_dist: _MetadataDistribution) -> Distribution:
        return Distribution(orig_dist.metadata["Name"], orig_dist.metadata["Version"])

    def __repr__(self) -> str:
        """Return a string representation of the translator."""
        return f"{self.__class__.__name__}()"
