"""Contains the domain model."""
from __future__ import annotations

from abc import ABC
from typing import Container, Iterable, Optional


class ModularUnit(ABC, Container["ModularUnit"]):
    """Represents a modular unit used to organize Python code."""

    def __init__(self, file: str) -> None:
        """Initialize the modular unit."""
        self._file = file

    @property
    def file(self) -> Optional[str]:
        """Return the file of the unit."""
        return self._file

    def __contains__(self, other: object) -> bool:
        """Return true if the unit is part of this unit or any sub-units."""
        return isinstance(other, self.__class__) and other == self

    def __eq__(self, other: object) -> bool:
        """Return true if both units have the same file."""
        return isinstance(other, self.__class__) and self.file == other.file

    def __hash__(self) -> int:
        """Create a hash of the unit."""
        return hash(self.file)

    def __repr__(self) -> str:
        """Return a string representation of the unit."""
        return f"{self.__class__.__name__}(file={repr(self.file)})"


class Module(ModularUnit):  # pylint: disable=too-few-public-methods
    """Represents a Python module."""


class Package(ModularUnit):
    """Represents a Python package."""

    def __init__(self, file: str, units: Optional[Iterable[ModularUnit]] = None) -> None:
        """Initialize distribution."""
        super().__init__(file)
        self._units = frozenset(units) if units else frozenset()

    def __contains__(self, other: object) -> bool:
        """Return true if the unit is part of this unit or any sub-units."""
        return super().__contains__(other) or any(other in u for u in self._units)

    def __eq__(self, other: object) -> bool:
        """Return true if both packages have the same file and units."""
        return super().__eq__(other) and self._units == other._units  # type: ignore

    def __hash__(self) -> int:
        """Create a hash of the package."""
        return hash((super().__hash__(), self._units))


class Distribution(Container[Package]):
    """Represents a Python distribution."""

    def __init__(self, name: str, version: str, packages: Iterable[Package]) -> None:
        """Initialize the distribution."""
        self._name = name
        self._version = version
        self._packages = frozenset(packages)

    @property
    def name(self) -> str:
        """Return the name of the distribution."""
        return self._name

    @property
    def version(self) -> str:
        """Return the version of the distribution."""
        return self._version

    def __contains__(self, other: object) -> bool:
        """Return true if the unit is part of the distribution."""
        return isinstance(other, ModularUnit) and any(other in p for p in self._packages)

    def __eq__(self, other: object) -> bool:
        """Return true if both distributions have the same name, version and packages."""
        return (
            isinstance(other, self.__class__)
            and self.name == other.name
            and self.version == other.version
            and self._packages == other._packages
        )

    def __hash__(self) -> int:
        """Create a hash of the distribution."""
        return hash((self.name, self.version, self._packages))

    def __repr__(self) -> str:
        """Return a string representation of the distribution."""
        return f"{self.__class__.__name__}(name={repr(self.name)}, version={repr(self.version)})"
