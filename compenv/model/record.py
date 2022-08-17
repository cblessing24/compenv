"""Contains the record class and its constituents."""
from __future__ import annotations

import textwrap
from dataclasses import asdict, dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class Record:
    """Represents a record of the environment."""

    distributions: Distributions

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
        return "Distributions:" + "\n" + textwrap.indent("\n".join(sorted(lines)), " " * 4)


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
