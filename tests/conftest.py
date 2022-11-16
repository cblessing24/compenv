from __future__ import annotations

from typing import Iterable, Optional, Protocol, Union

import pytest

from compenv.model.computation import AlgorithmName, Arguments, Computation, Specification
from compenv.model.environment import Environment
from compenv.model.record import Distribution


class ComputationCreator(Protocol):
    def __call__(
        self,
        algorithm_name: str,
        arguments: str,
        *,
        environment: Optional[Union[Iterable[tuple[str, str]], Environment]] = None,
    ) -> Computation:
        ...


@pytest.fixture
def create_computation(create_environment: EnvironmentCreator) -> ComputationCreator:
    def create(
        algorithm_name: str,
        arguments: str,
        *,
        environment: Optional[Union[Iterable[tuple[str, str]], Environment]] = None,
    ) -> Computation:
        if not isinstance(environment, Environment):
            environment = create_environment(environment)
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
