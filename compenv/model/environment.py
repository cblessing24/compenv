"""Contains model objects related to the computational environment."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .record import Distribution


@dataclass(frozen=True)
class Environment:
    """A set of external factors that could (potentially) influence the outcome of a computation."""

    distributions: frozenset[Distribution] = field(default_factory=frozenset)


class EnvironmentDeterminingService(ABC):  # pylint: disable=too-few-public-methods
    """A service that is able to determine the environment."""

    @abstractmethod
    def determine(self) -> Environment:
        """Determine the environment."""
