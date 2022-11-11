from __future__ import annotations

from typing import Callable, Iterable, Optional, Protocol

import pytest

from compenv.model.computation import AlgorithmName, Arguments, Computation, Specification
from compenv.model.environment import Environment
from compenv.model.record import Distribution

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
