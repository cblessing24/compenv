"""Contains the domain model."""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from types import TracebackType
from typing import Callable, ContextManager, Optional, Type

from . import record
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


class Environment:
    """Represents the current execution environment."""

    @staticmethod
    def record() -> Record:
        """Record information about the current execution environment."""
        installed_dists = frozenset(record.get_installed_distributions())
        active_modules = frozenset(record.get_active_modules())
        active_dists = frozenset(id for id in installed_dists if id & active_modules)
        return Record(
            installed_distributions=installed_dists, active_distributions=active_dists, active_modules=active_modules
        )

    def consistency_check(self) -> _ConsistencyCheck:
        """Return a context manager used to check the environment's consistency during code execution."""
        return _ConsistencyCheck(self)

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"{self.__class__.__name__}()"


class _ConsistencyCheck(ContextManager):
    """Context manager used to check whether the environment stayed consistent during execution of the with block."""

    def __init__(self, environment: Environment) -> None:
        """Initialize the environment consistency check."""
        self._environment = environment
        self._success: Optional[bool] = None
        self._record_before: Optional[Record] = None
        self._record_after: Optional[Record] = None

    @property
    def success(self) -> bool:
        """Return the result of the environment consistency check."""
        if self._success is None:
            raise RuntimeError("Can not access 'success' attribute while still in with block!")
        return self._success

    @property
    def record(self) -> Record:
        """Return the final record that was created in the check."""
        if not self._record_after:
            raise RuntimeError("Can not access 'record' attribute while still in with block!")
        return self._record_after

    def __enter__(self) -> _ConsistencyCheck:
        """Enter the block in which the consistency of the environment will be checked."""
        self._record_before = self._environment.record()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Exit the block in which the consistency of the environment will be checked."""
        self._record_after = self._environment.record()
        self._success = self._record_before == self._record_after

    def __repr__(self) -> str:
        """Return a string representation of the consistency check."""
        return f"{self.__class__.__name__}(environment={repr(self._environment)})"
