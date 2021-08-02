"""Contains the domain model."""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Callable

from .environment import Environment
from .record import Record


class Computation:
    """Represents a computation."""

    def __init__(
        self,
        identifier: str,
        environment: Environment,
        trigger: Callable[[], None],
    ) -> None:
        """Initialize the computation."""
        self.identifier = identifier
        self._environment = environment
        self._trigger = trigger
        self._is_executed = False

    def execute(self) -> ComputationRecord:
        """Execute the computation."""
        if self._is_executed:
            raise RuntimeError("Computation already executed!")
        with self._environment.consistency_check() as check:
            self._trigger()
        if not check.success:
            warnings.warn("Environment changed during execution!")
        self._is_executed = True
        return ComputationRecord(self.identifier, check.record)

    def __repr__(self) -> str:
        """Return a string representation of the computation."""
        return (
            f"{self.__class__.__name__}("
            f"identifier={repr(self.identifier)}, "
            f"environment={repr(self._environment)}, "
            f"trigger={repr(self._trigger)})"
        )


@dataclass(frozen=True)
class ComputationRecord:
    """Represents the association between an executed computation and its environmental record."""

    identifier: str
    record: Record
