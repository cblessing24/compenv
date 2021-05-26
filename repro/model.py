"""Contains the domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Module:
    """An imported module."""

    name: str
    file: Optional[str]


@dataclass(frozen=True)
class Distribution:
    """An installed Distribution."""

    name: str
    version: str
    files: set[str]
