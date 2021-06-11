"""Contains the domain model."""
from collections.abc import Set
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, TypeVar


@dataclass(frozen=True)
class Module:
    """Represents a Python module."""

    file: Path


_T = TypeVar("_T")


@dataclass(frozen=True)
class Distribution(Set[Module]):
    """Represents a Python distribution."""

    name: str
    version: str
    modules: frozenset[Module] = field(default_factory=frozenset)

    def __contains__(self, other: object) -> bool:
        """Check if module is part of this distribution."""
        return other in self.modules

    def __iter__(self) -> Iterator[Module]:
        """Iterate over the modules belonging to this distribution."""
        for module in self.modules:
            yield module

    def __len__(self) -> int:
        """Return the number of modules belonging to this distribution."""
        return len(self.modules)

    @classmethod
    def _from_iterable(cls, it: Iterable[_T]) -> frozenset[_T]:
        """Construct a frozen set from any iterable.

        This method is necessary to make the set methods "__and__", "__or__", "__sub__" and "__xor__" work.
        """
        return frozenset(it)
