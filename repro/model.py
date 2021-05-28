"""Contains the domain model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Collection, Iterator, Optional


@dataclass(frozen=True)
class Module:
    """An imported module."""

    name: str
    file: Optional[str] = None


@dataclass(frozen=True, init=False)
class Distribution(Collection[Module]):
    """An installed Distribution."""

    name: str
    version: str
    _modules: set[Module] = field(repr=False)

    def __init__(self, name, version, modules) -> None:
        """Initialize distribution."""
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "_modules", modules)

    def __contains__(self, module: object) -> bool:
        """Return true if the module is part of the distribution, false otherwise."""
        if not isinstance(module, Module):
            return False
        return module in self._modules

    def __len__(self) -> int:
        """Return the number of modules in the distribution."""
        return len(self._modules)

    def __iter__(self) -> Iterator[Module]:
        """Iterate over modules in the distribution."""
        return iter(self._modules)
