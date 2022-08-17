"""Contains the record use-case."""
import dataclasses
from typing import Callable

from ..model.computation import Temp
from ..model.record import ComputationRecord, Identifier
from .abstract import DistributionFinder, Repository, Request, Response, Service


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

    def __init__(
        self,
        *,
        output_port: Callable[[RecordResponse], None],
        repo: Repository,
        distribution_finder: DistributionFinder,
    ) -> None:
        """Initialize the service."""
        super().__init__(output_port=output_port)
        self.repo = repo
        self.distribution_finder = distribution_finder

    def _execute(self, request: RecordRequest) -> RecordResponse:
        """Record the environment."""
        distributions = self.distribution_finder()
        record = ComputationRecord(request.identifier, distributions)
        request.trigger()
        computation_record = Temp(request.identifier, record)
        self.repo.add(computation_record)
        return self._response_cls()

    def __repr__(self) -> str:
        """Return a string representation of the record service."""
        return f"{self.__class__.__name__}(output_port={self.output_port!r}, repo={self.repo!r})"
