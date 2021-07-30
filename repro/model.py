"""Contains the domain model."""
from __future__ import annotations

import textwrap
import warnings
from collections.abc import Set
from dataclasses import asdict, dataclass, field
from pathlib import Path
from types import TracebackType
from typing import Callable, ContextManager, Iterable, Iterator, Optional, Type, TypeVar

get_active_modules: Callable[[], Iterable[Module]]
get_installed_distributions: Callable[[], Iterable[Distribution]]


@dataclass(frozen=True, order=True)
class Module:
    """Represents a Python module."""

    file: Path


_T = TypeVar("_T")


@dataclass(frozen=True, order=True)
class Distribution(Set[Module]):  # type: ignore[override]
    """Represents a Python distribution."""

    name: str
    version: str
    modules: frozenset[Module] = field(default_factory=frozenset)

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
        installed_dists = frozenset(get_installed_distributions())
        active_modules = frozenset(get_active_modules())
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


@dataclass(frozen=True)
class Record:
    """Represents a record of the environment."""

    installed_distributions: frozenset[Distribution]
    active_distributions: frozenset[Distribution]
    active_modules: frozenset[Module]

    def __str__(self) -> str:
        """Return a human-readable representation of the record."""
        indent = 4 * " "
        attr_names = asdict(self).keys()
        methods = {n.replace("_", " "): getattr(self, f"_convert_{n}_to_strings") for n in attr_names}
        section_parts = {n: m() for n, m in methods.items()}
        sections = [("\n" + 2 * indent).join([n + ":"] + sp) for n, sp in section_parts.items()]
        joined_sections = ("\n" + indent).join(sections)
        return "Record:\n" + indent + joined_sections

    def _convert_installed_distributions_to_strings(self) -> list[str]:
        return self._convert_distributions_to_strings(self.installed_distributions)

    def _convert_active_distributions_to_strings(self) -> list[str]:
        return self._convert_distributions_to_strings(self.active_distributions)

    @staticmethod
    def _convert_distributions_to_strings(dists: Iterable[Distribution]) -> list[str]:
        return [f"{d.name} ({d.version})" for d in sorted(dists)]

    def _convert_active_modules_to_strings(self) -> list[str]:
        return [str(m.file) for m in sorted(self.active_modules)]
