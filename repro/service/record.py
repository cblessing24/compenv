"""Contains the record use-case."""
from collections.abc import Callable

from ..model.computation import Computation, Identifier
from ..model.environment import Environment
from .abstract import ComputationRecordRepository


def record(repo: ComputationRecordRepository, identifier: Identifier, trigger: Callable[[], None]) -> None:
    """Record the environment."""
    computation = Computation(identifier, environment=Environment(), trigger=trigger)
    repo[identifier] = computation.execute()
