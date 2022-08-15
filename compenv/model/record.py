"""Contains the record class and its constituents."""
from __future__ import annotations

import textwrap
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import FrozenSet

get_installed_distributions: Callable[[], InstalledDistributions]


@dataclass(frozen=True)
class Record:
    """Represents a record of the environment."""

    installed_distributions: InstalledDistributions

    def __str__(self) -> str:
        """Return a human-readable representation of the record."""
        indent = 4 * " "
        attr_names = asdict(self).keys()
        sections = [str(getattr(self, n)) for n in attr_names]
        sections = [textwrap.indent(s, indent) for s in sections]
        return "Record:\n" + "\n".join(sections)


class Distributions(FrozenSet["Distribution"]):
    """Represents a set of distributions."""

    def __str__(self) -> str:
        """Return a human-readable representation of the set of distributions."""
        max_name_length = max(len(d.name) for d in self)
        lines = [f"{d.name:<{max_name_length}} ({d.version})" for d in self]
        return "\n".join(sorted(lines))


class InstalledDistributions(Distributions):
    """Represents the set of all installed distributions."""

    def __str__(self) -> str:
        """Return a human-readable representation of the set of installed distributions."""
        return "Installed Distributions:\n" + textwrap.indent(super().__str__(), " " * 4)


@dataclass(frozen=True)
class Distribution:
    """Represents a Python distribution."""

    name: str
    version: str

    def __str__(self) -> str:
        """Return a human-readable representation of the object."""
        return textwrap.dedent(
            f"""
            Distribution:
                name: {self.name}
                version: {self.version}
            """
        ).strip()
