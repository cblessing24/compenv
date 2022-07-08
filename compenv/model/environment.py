"""Contains environment related code."""
from __future__ import annotations

from types import TracebackType
from typing import ContextManager, Optional, Type

from . import record
from .record import ActiveModules, InstalledDistributions, Record


class Environment:
    """Represents the current execution environment."""

    @staticmethod
    def record() -> Record:
        """Record information about the current execution environment."""
        installed_dists = InstalledDistributions(record.get_installed_distributions())
        active_modules = ActiveModules(record.get_active_modules())
        return Record(installed_distributions=installed_dists, active_modules=active_modules)

    def consistency_check(self) -> _ConsistencyCheck:
        """Return a context manager used to check the environment's consistency during code execution."""
        return _ConsistencyCheck(self)

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"{self.__class__.__name__}()"


class _ConsistencyCheck(ContextManager["_ConsistencyCheck"]):
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
