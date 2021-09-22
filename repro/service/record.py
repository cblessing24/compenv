"""Contains the record use-case."""
import dataclasses
from typing import Callable

from ..model.computation import Computation, Identifier
from ..model.environment import Environment
from .abstract import Request, Service


@dataclasses.dataclass(frozen=True)
class RecordRequest(Request):
    """Request for the record service."""

    identifier: Identifier
    trigger: Callable[[], None]


class RecordService(Service[RecordRequest]):
    """A service used to record the environment."""

    _request_cls = RecordRequest

    def __call__(self, request: RecordRequest) -> None:
        """Record the environment."""
        computation = Computation(
            request.identifier,
            environment=Environment(),
            trigger=request.trigger,  # type: ignore (https://github.com/python/mypy/issues/6910#)
        )
        self.repo[request.identifier] = computation.execute()
