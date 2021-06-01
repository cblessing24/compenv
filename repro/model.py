"""Contains the domain model."""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Container, Optional


@dataclass(frozen=True)
class ModularUnit(ABC, Container["ModularUnit"]):
    """Represents a modular unit used to organize Python code."""

    name: str
    file: Optional[str]

    def __contains__(self, unit: object) -> bool:
        """Return true if the unit is part of this unit or any sub-units."""
        if not isinstance(unit, ModularUnit):
            raise TypeError
        return unit == self


@dataclass(frozen=True)
class Module(ModularUnit):
    """Represents a Python module."""


@dataclass(frozen=True, init=False)
class Package(ModularUnit):
    """Represents a Python package."""

    _units: frozenset[ModularUnit] = field(repr=False)

    def __init__(self, name, file, units):
        """Initialize distribution."""
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "file", file)
        object.__setattr__(self, "_units", units)

    def __contains__(self, unit: object) -> bool:
        """Return true if the unit is part of this unit or any sub-units."""
        return super().__contains__(unit) or any(unit in package_unit for package_unit in self._units)


@dataclass(frozen=True, init=False)
class Distribution(Container[Package]):
    """Represents a Python distribution."""

    name: str
    version: str
    _packages: frozenset[Package] = field(repr=False)

    def __init__(self, name, version, packages) -> None:
        """Initialize distribution."""
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "_packages", packages)

    def __contains__(self, unit: object) -> bool:
        """Return true if the unit is part of the distribution."""
        if not isinstance(unit, ModularUnit):
            raise TypeError
        return any(unit in p for p in self._packages)
