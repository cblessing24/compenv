"""Contains the record use-case."""
import dataclasses
from typing import Callable

from ..model.computation import Computation, Identifier
from ..model.environment import Environment
from .abstract import Request, Response, Service


@dataclasses.dataclass(frozen=True)
class RecordRequest(Request):
    """Request for the record service."""

    identifier: Identifier
    trigger: Callable[[], None]


@dataclasses.dataclass(frozen=True)
class RecordResponse(Response):
    """Response of the record service."""


class RecordService(Service[RecordRequest, RecordResponse]):  # pylint: disable=too-few-public-methods
    """A service used to record the environment."""

    _request_cls = RecordRequest
    _response_cls = RecordResponse

    def _execute(self, request: RecordRequest) -> RecordResponse:
        """Record the environment."""
        computation = Computation(
            request.identifier,
            environment=Environment(),
            trigger=request.trigger,  # type: ignore
        )
        self.repo[request.identifier] = computation.execute()
        return self._response_cls()
