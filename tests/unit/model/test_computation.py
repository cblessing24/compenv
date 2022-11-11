from __future__ import annotations

from typing import Callable, Iterable, Optional, Protocol

import pytest

from compenv.model.computation import (
    Algorithm,
    AlgorithmName,
    Arguments,
    Computation,
    ComputationRegistry,
    ComputationRegistryRepository,
    RecordingService,
    Specification,
)
from compenv.model.environment import Environment, EnvironmentDeterminingService
from compenv.model.record import Distribution


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
    environment = Environment()
    computation = algorithm.execute(environment, Arguments("myarguments"), fake_computation_trigger)
    assert computation == Computation(Specification(algorithm.name, Arguments("myarguments")), environment)


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
