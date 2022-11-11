from typing import Optional

import pytest

from compenv.model.computation import (
    AlgorithmName,
    Arguments,
    Computation,
    ComputationRegistry,
    ComputationRegistryRepository,
    RecordingService,
    Specification,
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
    environment = Environment()
    environment_determining_service = FakeEnvironmentDeterminingService(environment)
    recording_service = RecordingService(
        computation_registry_repository=repository, environment_determining_service=environment_determining_service
    )

    recording_service.record(algorithm_name=algorithm_name, arguments=arguments, trigger=fake_computation_trigger)

    assert fake_computation_trigger.arguments == arguments
    assert Computation(Specification(algorithm_name, arguments), environment) in repository.get(algorithm_name).list(
        environment
    )
