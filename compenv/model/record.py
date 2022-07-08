"""Contains the record class and its constituents."""
from __future__ import annotations

import itertools
import textwrap
from collections.abc import Callable, Iterable, Iterator
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import AbstractSet, FrozenSet, TypeVar

get_active_modules: Callable[[], ActiveModules]
get_installed_distributions: Callable[[], InstalledDistributions]


@dataclass(frozen=True)
class Record:
    """Represents a record of the environment."""

    installed_distributions: InstalledDistributions
    active_modules: ActiveModules

    @property
    def modules(self) -> Modules:
        """Return all modules in the record, i.e. active ones and those belonging to a distribution."""
        return Modules(self.installed_distributions.modules.union(self.active_modules))

    def __str__(self) -> str:
        """Return a human-readable representation of the record."""
        indent = 4 * " "
        attr_names = asdict(self).keys()
        sections = [str(getattr(self, n)) for n in attr_names]
        sections = [textwrap.indent(s, indent) for s in sections]
        return "Record:\n" + "\n".join(sections)


class Distributions(FrozenSet["Distribution"]):
    """Represents a set of distributions."""

    @property
    def modules(self) -> Modules:
        """Return all modules belonging to a distribution."""
        return Modules(itertools.chain(*self))

    def __str__(self) -> str:
        """Return a human-readable representation of the set of distributions."""
        max_name_length = max(len(d.name) for d in self)
        lines = [f"{'+' if d.is_active else '-'} {d.name:<{max_name_length}} ({d.version})" for d in self]
        return "\n".join(sorted(lines))


class ActiveDistributions(Distributions):
    """Represents the set of all active distributions."""

    def __str__(self) -> str:
        """Return a human-readable representation of the set of active distributions."""
        return "Active Distributions:\n" + textwrap.indent(super().__str__(), " " * 4)


class InstalledDistributions(Distributions):
    """Represents the set of all installed distributions."""

    @property
    def active(self) -> ActiveDistributions:
        """Return all installed distributions that are active."""
        return ActiveDistributions({d for d in self if d.is_active})

    def __str__(self) -> str:
        """Return a human-readable representation of the set of installed distributions."""
        return "Installed Distributions:\n" + textwrap.indent(super().__str__(), " " * 4)


class Modules(FrozenSet["Module"]):
    """Represents a set of modules."""

    def __str__(self) -> str:
        """Return a human-readable representation of the set."""
        return "\n".join(sorted(str(m.file) for m in self))


_T = TypeVar("_T")


@dataclass(frozen=True, order=True)
class Distribution(AbstractSet["Module"]):  # type: ignore[override]
    """Represents a Python distribution."""

    name: str
    version: str
    modules: Modules = field(default_factory=Modules)

    @property
    def is_active(self) -> bool:
        """Return True if one of the distribution's modules is active, False otherwise."""
        return any(m.is_active for m in self.modules)

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
        ).strip()
        return string + "\n" + textwrap.indent(str(self.modules), " " * 8)

    @classmethod
    def _from_iterable(cls, it: Iterable[_T]) -> frozenset[_T]:
        """Construct a frozen set from any iterable.

        This method is necessary to make the set methods "__and__", "__or__", "__sub__" and "__xor__" work.
        """
        return frozenset(it)


class ActiveModules(Modules):
    """Represents the set of all active moduls."""

    def __str__(self) -> str:
        """Return a human-readable representation of the set of active modules."""
        return "Active Modules:\n" + textwrap.indent(super().__str__(), " " * 4)


@dataclass(frozen=True, order=True)
class Module:
    """Represents a Python module."""

    file: Path
    is_active: bool
