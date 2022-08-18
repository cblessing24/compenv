"""Contains the record class and its constituents."""
from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import NewType

Identifier = NewType("Identifier", str)


INDENT = 4 * " "


@dataclass(frozen=True)
class ComputationRecord:
    """Represents a record of the environment."""

    identifier: Identifier
    distributions: frozenset[Distribution]

    def __str__(self) -> str:
        """Return a human-readable representation of the record."""
        max_name_length = max(len(d.name) for d in self.distributions)
        lines = [f"{d.name:<{max_name_length}} ({d.version})" for d in self.distributions]
        distributions_string = "Distributions:" + "\n" + textwrap.indent("\n".join(sorted(lines)), INDENT)
        return f"Computation Record:\n{textwrap.indent(distributions_string, INDENT)}"


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
