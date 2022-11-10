"""Contains model objects related to computation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, NewType, Optional

from .environment import Environment

AlgorithmName = NewType("AlgorithmName", str)
Arguments = NewType("Arguments", str)


@dataclass(frozen=True)
class Computation:
    """The execution of a particular algorithm on a particular set of arguments in a particular environment."""

    algorithm: AlgorithmName
    arguments: Arguments
    environment: Environment


class Algorithm:
    """Something that produces an output given some inputs."""

    def __init__(
        self, name: AlgorithmName, computations: Optional[Mapping[Environment, Iterable[Computation]]] = None
    ) -> None:
        """Initialize the algorithm."""
        self.name = name
        if computations is None:
            computations = {}
        self._computations = defaultdict(set, ((k, set(v)) for k, v in computations.items()))

    def execute(self, environment: Environment, arguments: Arguments) -> None:
        """Execute the algorithm in the given environment using the provided arguments."""
        self._computations[environment].add(Computation(self.name, arguments, environment))

    def __getitem__(self, environment: Environment) -> frozenset[Computation]:
        """Get all computations of the algorithm in the given environment."""
        return frozenset(self._computations[environment])


class AlgorithmRepository(ABC):
    """A repository containing algorithms."""

    @abstractmethod
    def add(self, algorithm: Algorithm) -> None:
        """Add an algorithm to the repository."""

    @abstractmethod
    def get(self, name: AlgorithmName) -> Algorithm:
        """Get the algorithm with the given name."""


class EnvironmentDeterminingService(ABC):  # pylint: disable=too-few-public-methods
    """A service that is able to determine the environment."""

    @abstractmethod
    def determine(self) -> Environment:
        """Determine the environment."""


class RecordingService:  # pylint: disable=too-few-public-methods
    """A service that is able to record the environment during a computation."""

    def __init__(
        self, algorithm_repository: AlgorithmRepository, environment_determining_service: EnvironmentDeterminingService
    ) -> None:
        """Initialize the recording service."""
        self.algorithm_repository = algorithm_repository
        self.environment_determining_service = environment_determining_service

    def record(self, algorithm_name: AlgorithmName, arguments: Arguments, trigger: Callable[[Arguments], None]) -> None:
        """Record the environment during the execution of the algorithm on the given arguments."""
        trigger(arguments)
        algorithm = self.algorithm_repository.get(algorithm_name)
        environment = self.environment_determining_service.determine()
        algorithm.execute(environment, arguments)
