"""Contains the record class and its constituents."""
from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import FrozenSet, NewType

Identifier = NewType("Identifier", str)


INDENT = 4 * " "


@dataclass(frozen=True)
class ComputationRecord:
    """Represents a record of the environment."""

    identifier: Identifier
    distributions: Distributions

    def __str__(self) -> str:
        """Return a human-readable representation of the record."""
        return f"Computation Record:\n{textwrap.indent(str(self.distributions), INDENT)}"


class Distributions(FrozenSet["Distribution"]):
    """Represents a set of distributions."""

    def __str__(self) -> str:
        """Return a human-readable representation of the set of distributions."""
        max_name_length = max(len(d.name) for d in self)
        lines = [f"{d.name:<{max_name_length}} ({d.version})" for d in self]
        return "Distributions:" + "\n" + textwrap.indent("\n".join(sorted(lines)), INDENT)


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
