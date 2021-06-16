"""Contains the domain model."""
from __future__ import annotations

import textwrap
from collections.abc import Set
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Iterator, TypeVar

get_loaded_modules: Callable[[], Iterable[Module]]
get_installed_distributions: Callable[[], Iterable[Distribution]]


@dataclass(frozen=True, order=True)
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

    def __str__(self) -> str:
        """Return a human-readable representation of the object."""
        string = textwrap.dedent(
            f"""
            Distribution:
                name: {self.name}
                version: {self.version}
                modules:
            """
        )
        indent = 8 * " "
        module_strings = ("\n" + indent).join(str(m.file) for m in sorted(self.modules))
        return (string + indent + module_strings).strip()

    @classmethod
    def _from_iterable(cls, it: Iterable[_T]) -> frozenset[_T]:
        """Construct a frozen set from any iterable.

        This method is necessary to make the set methods "__and__", "__or__", "__sub__" and "__xor__" work.
        """
        return frozenset(it)


def get_active_distributions() -> frozenset[Distribution]:
    """Get all currently active distributions, i.e. all distributions that have at least one of their modules loaded."""
    loaded_modules = frozenset(get_loaded_modules())
    installed_dists = get_installed_distributions()
    return frozenset(id for id in installed_dists if id & loaded_modules)
