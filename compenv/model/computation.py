"""Contains model objects related to computation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable, NewType, Optional

from .environment import Environment, EnvironmentDeterminingService

AlgorithmName = NewType("AlgorithmName", str)
Arguments = NewType("Arguments", str)


@dataclass(frozen=True)
class Computation:
    """The execution of a particular computation specification in a particular environment."""

    specification: Specification
    environment: Environment


@dataclass(frozen=True)
class Specification:
    """The Specification for a particular computation."""

    algorithm_name: AlgorithmName
    arguments: Arguments


class Algorithm:  # pylint: disable=too-few-public-methods
    """Something that produces an output given some inputs."""

    def __init__(self, name: AlgorithmName) -> None:
        """Initialize the algorithm."""
        self.name = name

    def execute(
        self, environment: Environment, arguments: Arguments, trigger: Callable[[Arguments], None]
    ) -> Computation:
        """Execute the algorithm in the given environment using the provided arguments."""
        trigger(arguments)
        return Computation(Specification(self.name, arguments), environment)


class ComputationRegistryRepository(ABC):
    """A repository containing computation registries."""

    @abstractmethod
    def add(self, registry: ComputationRegistry) -> None:
        """Add a registry to the repository."""

    @abstractmethod
    def get(self, algorithm_name: AlgorithmName) -> ComputationRegistry:
        """Get the registry for the given algorithm name."""


class RecordingService:  # pylint: disable=too-few-public-methods
    """A service that is able to record the environment during a computation."""

    def __init__(
        self,
        computation_registry_repository: ComputationRegistryRepository,
        environment_determining_service: EnvironmentDeterminingService,
    ) -> None:
        """Initialize the recording service."""
        self.computation_registry_repository = computation_registry_repository
        self.environment_determining_service = environment_determining_service

    def record(self, algorithm_name: AlgorithmName, arguments: Arguments, trigger: Callable[[Arguments], None]) -> None:
        """Record the environment during the execution of the algorithm on the given arguments."""
        environment = self.environment_determining_service.determine()
        registry = self.computation_registry_repository.get(algorithm_name)
        computation = Algorithm(algorithm_name).execute(environment, arguments, trigger)
        registry.add(computation)


class ComputationRegistry:
    """A registry associating computations with the environments in which the were executed."""

    def __init__(self, algorithm_name: AlgorithmName, computations: Optional[Iterable[Computation]] = None) -> None:
        """Initialize the registry."""
        self.algorithm_name = algorithm_name
        if computations is None:
            computations = []
        self._computations: dict[Environment, set[Computation]] = defaultdict(set)
        for computation in computations:
            self.add(computation)

    def add(self, computation: Computation) -> None:
        """Add a computation to the registry."""
        if computation.specification.algorithm_name != self.algorithm_name:
            raise ValueError(
                f"Expected {repr(self.algorithm_name)} for algorithm name of computation, "
                f"got {repr(computation.specification.algorithm_name)}"
            )
        self._computations[computation.environment].add(computation)

    def list(self, environment: Environment) -> frozenset[Computation]:
        """List all computations that were executed in the given environment."""
        return frozenset(self._computations[environment])
