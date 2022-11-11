from typing import Optional

from compenv.model.computation import (
    AlgorithmName,
    Arguments,
    ComputationRegistry,
    ComputationRegistryRepository,
    RecordingService,
)
from compenv.model.environment import Environment, EnvironmentDeterminingService

from ...conftest import ComputationCreator, EnvironmentCreator


def test_can_record_computation(
    create_computation: ComputationCreator,
    create_environment: EnvironmentCreator,
) -> None:
    class FakeComputationTrigger:
        def __init__(self) -> None:
            self.arguments: Optional[Arguments] = None

        def __call__(self, arguments: Arguments) -> None:
            self.arguments = arguments

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

    environment = create_environment()
    computation = create_computation("myalgorithm", "myarguments", environment)
    repository = FakeComputationRegistryRepository()
    repository.add(ComputationRegistry(computation.specification.algorithm_name))
    arguments = Arguments("myarguments")
    environment_determining_service = FakeEnvironmentDeterminingService(environment)
    trigger = FakeComputationTrigger()
    recording_service = RecordingService(
        computation_registry_repository=repository, environment_determining_service=environment_determining_service
    )

    recording_service.record(
        algorithm_name=computation.specification.algorithm_name,
        arguments=computation.specification.arguments,
        trigger=trigger,
    )

    assert trigger.arguments == arguments
    assert computation == repository.get(computation.specification.algorithm_name).get(computation.specification)
