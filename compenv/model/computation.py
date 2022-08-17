"""Contains code related to computations."""
from __future__ import annotations

import textwrap
from dataclasses import dataclass

from .record import Identifier, Record


@dataclass(frozen=True)
class ComputationRecord:
    """Represents the association between an executed computation and its environmental record."""

    identifier: Identifier
    record: Record

    def __str__(self) -> str:
        """Return a human-readable representation of the computation record."""
        indent = 4 * " "
        string = "Computation Record:\n"
        string += textwrap.indent("Identifier: " + self.identifier + "\n" + str(self.record), indent)
        return string
