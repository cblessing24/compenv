"""Contains model objects related to the computational environment."""
from __future__ import annotations

from dataclasses import dataclass

from .record import Distribution


@dataclass(frozen=True)
class Environment:
    """A set of external factors that could (potentially) influence the outcome of a computation."""

    distributions: frozenset[Distribution]
