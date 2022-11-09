"""Contains model objects related to computation."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import NewType

from .environment import Environment

AlgorithmName = NewType("AlgorithmName", str)
ArgumentsHash = NewType("ArgumentsHash", str)


@dataclass(frozen=True)
class Computation:
    """The execution of a particular algorithm on a particular set of arguments in a particular environment."""

    algorithm: AlgorithmName
    arguments: ArgumentsHash
    environment: Environment


class Algorithm:
    """Something that produces an output given some inputs."""

    def __init__(self, name: AlgorithmName) -> None:
        """Initialize the algorithm."""
        self.name = name
        self._computations: dict[Environment, set[Computation]] = defaultdict(set)

    def execute(self, environment: Environment, arguments: ArgumentsHash) -> None:
        """Execute the algorithm in the given environment using the provided arguments."""
        self._computations[environment].add(Computation(self.name, arguments, environment))

    def __getitem__(self, environment: Environment) -> frozenset[Computation]:
        """Get all computations of the algorithm in the given environment."""
        return frozenset(self._computations[environment])
