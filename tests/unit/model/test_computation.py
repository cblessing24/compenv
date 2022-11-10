from __future__ import annotations

from typing import Optional

import pytest

from compenv.model.computation import (
    Algorithm,
    AlgorithmName,
    AlgorithmRepository,
    Arguments,
    Computation,
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


def test_executing_algorithm_records_computation() -> None:
    algorithm = Algorithm(AlgorithmName("myalgorithm"))
    environment = Environment(frozenset())
    algorithm.execute(environment, Arguments("myarguments"))
    assert algorithm[environment] == frozenset(
        [Computation(AlgorithmName("myalgorithm"), Arguments("myarguments"), environment)]
    )


def test_algorithm_has_name_attribute() -> None:
    assert Algorithm(AlgorithmName("myalgorithm")).name == AlgorithmName("myalgorithm")


def test_can_instantiate_with_computations() -> None:
    environment = Environment(frozenset())
    computation = Computation(AlgorithmName("myalgorithm"), Arguments("myarguments"), environment)
    algorithm = Algorithm(
        AlgorithmName("myalgorithm"),
        computations={environment: [computation]},
    )
    assert algorithm[environment] == frozenset([computation])


def test_can_record_computation(fake_computation_trigger: FakeComputationTrigger) -> None:
    class FakeAlgorithmRepository(AlgorithmRepository):
        def __init__(self) -> None:
            self.algorithms: dict[AlgorithmName, Algorithm] = {}

        def add(self, algorithm: Algorithm) -> None:
            self.algorithms[algorithm.name] = algorithm

        def get(self, name: AlgorithmName) -> Algorithm:
            return self.algorithms[name]

    class FakeEnvironmentDeterminingService(EnvironmentDeterminingService):
        def __init__(self, environment: Environment) -> None:
            self.environment = environment

        def determine(self) -> Environment:
            return self.environment

    algorithm_name = AlgorithmName("myalgorithm")
    repository = FakeAlgorithmRepository()
    repository.add(Algorithm(algorithm_name))
    arguments = Arguments("myarguments")
    environment = Environment(frozenset())
    environment_determining_service = FakeEnvironmentDeterminingService(environment)
    recording_service = RecordingService(
        algorithm_repository=repository, environment_determining_service=environment_determining_service
    )

    recording_service.record(algorithm_name=algorithm_name, arguments=arguments, trigger=fake_computation_trigger)

    assert fake_computation_trigger.arguments == arguments
    assert repository.get(algorithm_name)[environment] == frozenset(
        [Computation(algorithm_name, arguments, environment)]
    )
