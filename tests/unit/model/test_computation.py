from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Optional, Protocol

import pytest

from compenv.model.computation import Algorithm, AlgorithmName, Computation, ComputationRegistry

from ...conftest import ComputationCreator, EnvironmentCreator


def test_algorithm_has_name_attribute() -> None:
    assert Algorithm(AlgorithmName("myalgorithm")).name == AlgorithmName("myalgorithm")


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
    create_computation: ComputationCreator, create_registry: RegistryCreator, create_environment: EnvironmentCreator
) -> None:
    computation = create_computation("myalgorithm", "myarguments", create_environment())
    registry = create_registry("myalgorithm", [computation])
    with pytest.raises(ValueError, match="Duplicate specification:"):
        registry.add(replace(computation, environment=create_environment([("mydistribution", "0.1.1")])))


def test_can_list_computations(
    create_computation: ComputationCreator, create_registry: RegistryCreator, create_environment: EnvironmentCreator
) -> None:
    environment1 = create_environment()
    environment2 = create_environment([("mydistribution", "0.1.1")])
    computation1 = create_computation("myalgorithm", "myarguments1", environment1)
    computation2 = create_computation("myalgorithm", "myarguments2", environment2)
    registry = create_registry("myalgorithm", [computation1, computation2])
    assert set(registry.list()) == {computation1, computation2}


def test_can_list_computations_by_environment(
    create_computation: ComputationCreator, create_registry: RegistryCreator, create_environment: EnvironmentCreator
) -> None:
    environment1 = create_environment()
    environment2 = create_environment([("mydistribution", "0.1.1")])
    computation1 = create_computation("myalgorithm", "myarguments1", environment1)
    computation2 = create_computation("myalgorithm", "myarguments2", environment2)
    registry = create_registry("myalgorithm", [computation1, computation2])
    assert list(registry.list(environment1)) == [computation1]
