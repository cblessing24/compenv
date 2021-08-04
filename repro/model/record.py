"""Contains the record class and its constituents."""
from __future__ import annotations

import textwrap
from collections.abc import Callable, Iterable, Iterator, Set
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TypeVar

get_active_modules: Callable[[], Iterable[Module]]
get_installed_distributions: Callable[[], InstalledDistributions]


@dataclass(frozen=True)
class Record:
    """Represents a record of the environment."""

    installed_distributions: InstalledDistributions
    active_modules: ActiveModules

    def __str__(self) -> str:
        """Return a human-readable representation of the record."""
        indent = 4 * " "
        attr_names = asdict(self).keys()
        sections = [str(getattr(self, n)) for n in attr_names]
        sections = [textwrap.indent(s, indent) for s in sections]
        return "Record:\n" + "\n".join(sections)


class InstalledDistributions(frozenset["Distribution"]):
    """Represents the set of all installed distributions."""

    @property
    def active(self) -> frozenset[Distribution]:
        """Return all installed distributions that are active."""
        return frozenset({d for d in self if d.is_active})

    def __str__(self) -> str:
        """Return a human-readable representation of the set."""
        header = "Installed Distributions:"
        max_name_length = max(len(d.name) for d in self)
        indent = 4 * " "
        lines = [indent + f"{'+' if d.is_active else '-'} {d.name:<{max_name_length}} ({d.version})" for d in self]
        return "\n".join([header] + sorted(lines))


_T = TypeVar("_T")


@dataclass(frozen=True, order=True)
class Distribution(Set["Module"]):  # type: ignore[override]
    """Represents a Python distribution."""

    name: str
    version: str
    modules: frozenset[Module] = field(default_factory=frozenset)

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


class ActiveModules(frozenset["Module"]):
    """Represents the set of all active moduls."""

    def __str__(self) -> str:
        """Return a human-readable representation of the set."""
        header = "Active Modules:"
        indent = 4 * " "
        lines = [indent + str(m.file) for m in self]
        return "\n".join([header] + sorted(lines))


@dataclass(frozen=True, order=True)
class Module:
    """Represents a Python module."""

    file: Path
    is_active: bool
