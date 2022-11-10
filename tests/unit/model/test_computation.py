from __future__ import annotations

from typing import Optional

import pytest

from compenv.model.computation import (
    Algorithm,
    AlgorithmName,
    Arguments,
    Computation,
    ComputationRegistry,
    ComputationRegistryRepository,
    RecordingService,
)
from compenv.model.environment import Environment, EnvironmentDeterminingService


class FakeComputationTrigger:
    def __init__(self) -> None:
        self.arguments: Optional[Arguments] = None

    def __call__(self, arguments: Arguments) -> None:
        self.arguments = arguments


@pytest.fixture
def fake_computation_trigger() -> FakeComputationTrigger:
    return FakeComputationTrigger()


def test_executing_algorithm_records_computation(fake_computation_trigger: FakeComputationTrigger) -> None:
    algorithm = Algorithm(AlgorithmName("myalgorithm"))
    environment = Environment(frozenset())
    computation = algorithm.execute(environment, Arguments("myarguments"), fake_computation_trigger)
    assert computation == Computation(algorithm.name, Arguments("myarguments"), environment)


def test_algorithm_has_name_attribute() -> None:
    assert Algorithm(AlgorithmName("myalgorithm")).name == AlgorithmName("myalgorithm")


def test_can_record_computation(fake_computation_trigger: FakeComputationTrigger) -> None:
    class FakeComputationRegistryRepository(ComputationRegistryRepository):
        def __init__(self) -> None:
            self.registries: dict[AlgorithmName, ComputationRegistry] = {}

        def add(self, registry: ComputationRegistry) -> None:
            self.registries[registry.algorithm_name] = registry

        def get(self, name: AlgorithmName) -> ComputationRegistry:
            return self.registries[name]

    class FakeEnvironmentDeterminingService(EnvironmentDeterminingService):
        def __init__(self, environment: Environment) -> None:
            self.environment = environment

        def determine(self) -> Environment:
            return self.environment

    algorithm_name = AlgorithmName("myalgorithm")
    repository = FakeComputationRegistryRepository()
    repository.add(ComputationRegistry(algorithm_name))
    arguments = Arguments("myarguments")
    environment = Environment(frozenset())
    environment_determining_service = FakeEnvironmentDeterminingService(environment)
    recording_service = RecordingService(
        computation_registry_repository=repository, environment_determining_service=environment_determining_service
    )

    recording_service.record(algorithm_name=algorithm_name, arguments=arguments, trigger=fake_computation_trigger)

    assert fake_computation_trigger.arguments == arguments
    assert Computation(algorithm_name, arguments, environment) in repository.get(algorithm_name).list(environment)


def test_can_add_computation_to_registry() -> None:
    registry = ComputationRegistry(AlgorithmName("myalgorithm"))
    environment = Environment(frozenset())
    computation = Computation(AlgorithmName("myalgorithm"), Arguments("myarguments"), environment)
    registry.add(computation)
    assert computation in registry.list(environment)


def test_can_not_add_computation_produced_by_different_algorithm_to_registry() -> None:
    registry = ComputationRegistry(AlgorithmName("myalgorithm"))
    environment = Environment(frozenset())
    computation = Computation(AlgorithmName("myotheralgorithm"), Arguments("myarguments"), environment)
    with pytest.raises(ValueError, match="Expected '.*' for algorithm name of computation, got '.*'"):
        registry.add(computation)


def test_can_instantiate_registry_with_computations() -> None:
    environment = Environment(frozenset())
    computation = Computation(AlgorithmName("myalgorithm"), Arguments("myarguments"), environment)
    algorithm = ComputationRegistry(
        AlgorithmName("myalgorithm"),
        computations={computation},
    )
    assert algorithm.list(environment)
