from __future__ import annotations

from dataclasses import replace

import pytest

from compenv.model.computation import Algorithm, AlgorithmName

from ...conftest import ComputationCreator, EnvironmentCreator, RegistryCreator


def test_algorithm_has_name_attribute() -> None:
    assert Algorithm(AlgorithmName("myalgorithm")).name == AlgorithmName("myalgorithm")


def test_can_add_computation_to_registry(
    create_registry: RegistryCreator, create_computation: ComputationCreator
) -> None:
    registry = create_registry("myalgorithm")
    computation = create_computation("myalgorithm", "myarguments", environment=[])
    registry.add(computation)
    assert registry.get(computation.specification) == computation


def test_can_not_add_computation_produced_by_different_algorithms_to_registry(
    create_registry: RegistryCreator,
    create_computation: ComputationCreator,
) -> None:
    with pytest.raises(ValueError, match="Expected '.*' for algorithm name of computation, got '.*'"):
        create_registry("myalgorithm").add(create_computation("myotheralgorithm", "myarguments", environment=[]))


def test_can_not_add_computations_with_identical_specifications(
    create_computation: ComputationCreator, create_registry: RegistryCreator, create_environment: EnvironmentCreator
) -> None:
    computation = create_computation("myalgorithm", "myarguments", environment=[])
    registry = create_registry("myalgorithm", [computation])
    with pytest.raises(ValueError, match="Duplicate specification:"):
        registry.add(replace(computation, environment=create_environment([("mydistribution", "0.1.1")])))


def test_can_list_computations(create_computation: ComputationCreator, create_registry: RegistryCreator) -> None:
    computation1 = create_computation("myalgorithm", "myarguments1", environment=[])
    computation2 = create_computation("myalgorithm", "myarguments2", environment=[("mydistribution", "0.1.1")])
    registry = create_registry("myalgorithm", [computation1, computation2])
    assert set(registry.list()) == {computation1, computation2}


def test_can_list_computations_by_environment(
    create_computation: ComputationCreator, create_registry: RegistryCreator
) -> None:
    computation1 = create_computation("myalgorithm", "myarguments1", environment=[])
    computation2 = create_computation("myalgorithm", "myarguments2", environment=[("mydistribution", "0.1.1")])
    registry = create_registry("myalgorithm", [computation1, computation2])
    assert list(registry.list(computation1.environment)) == [computation1]
