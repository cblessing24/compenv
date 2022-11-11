from __future__ import annotations

from typing import Callable, Iterable, Optional, Protocol

import pytest

from compenv.model.computation import (
    Algorithm,
    AlgorithmName,
    Arguments,
    Computation,
    ComputationRegistry,
    Specification,
)
from compenv.model.environment import Environment
from compenv.model.record import Distribution


def test_algorithm_has_name_attribute() -> None:
    assert Algorithm(AlgorithmName("myalgorithm")).name == AlgorithmName("myalgorithm")


ComputationCreator = Callable[[str, str, Environment], Computation]


@pytest.fixture
def create_computation() -> ComputationCreator:
    def create(algorithm_name: str, arguments: str, environment: Environment) -> Computation:
        return Computation(Specification(AlgorithmName(algorithm_name), Arguments(arguments)), environment)

    return create


class EnvironmentCreator(Protocol):
    def __call__(self, distributions: Optional[Iterable[tuple[str, str]]] = ...) -> Environment:
        ...


@pytest.fixture
def create_environment() -> EnvironmentCreator:
    def create(distributions: Optional[Iterable[tuple[str, str]]] = None) -> Environment:
        if distributions is None:
            distributions = []
        return Environment(frozenset(Distribution(name, version) for (name, version) in distributions))

    return create


class RegistryCreator(Protocol):
    def __call__(self, algorithm_name: str, computations: Optional[Iterable[Computation]] = ...) -> ComputationRegistry:
        ...


@pytest.fixture
def create_registry() -> RegistryCreator:
    def create(algorithm_name: str, computations: Optional[Iterable[Computation]] = None) -> ComputationRegistry:
        return ComputationRegistry(AlgorithmName(algorithm_name), computations)

    return create


def test_can_add_computation_to_registry(
    create_registry: RegistryCreator, create_computation: ComputationCreator, create_environment: EnvironmentCreator
) -> None:
    registry = create_registry("myalgorithm")
    computation = create_computation("myalgorithm", "myarguments", create_environment())
    registry.add(computation)
    assert registry.get(computation.specification) == computation


def test_can_not_add_computation_produced_by_different_algorithms_to_registry(
    create_registry: RegistryCreator, create_computation: ComputationCreator, create_environment: EnvironmentCreator
) -> None:
    with pytest.raises(ValueError, match="Expected '.*' for algorithm name of computation, got '.*'"):
        create_registry("myalgorithm").add(create_computation("myotheralgorithm", "myarguments", create_environment()))


def test_can_not_add_computations_with_identical_specifications(
    create_registry: RegistryCreator, create_environment: EnvironmentCreator
) -> None:
    specification = Specification(AlgorithmName("myalgorithm"), Arguments("myarguments"))
    registry = create_registry("myalgorithm", [Computation(specification, create_environment())])
    with pytest.raises(ValueError, match="Duplicate specification:"):
        registry.add(Computation(specification, create_environment([("mydistribution", "0.1.1")])))
