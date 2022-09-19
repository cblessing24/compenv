"""Contains the record use-case."""
import dataclasses
from typing import Callable

from ..model.record import ComputationRecord, Identifier
from . import register_service_class
from .abstract import DistributionFinder, Request, Response, Service, UnitOfWork


@dataclasses.dataclass(frozen=True)
class RecordRequest(Request):
    """Request for the record service."""

    identifier: Identifier
    trigger: Callable[[], None]


@dataclasses.dataclass(frozen=True)
class RecordResponse(Response):
    """Response of the record service."""


@register_service_class
class RecordService(Service[RecordRequest, RecordResponse]):
    """A service used to record the environment."""

    name = "record"

    _request_cls = RecordRequest
    _response_cls = RecordResponse

    def __init__(
        self,
        *,
        output_port: Callable[[RecordResponse], None],
        uow: UnitOfWork,
        distribution_finder: DistributionFinder,
    ) -> None:
        """Initialize the service."""
        super().__init__(output_port=output_port)
        self.uow = uow
        self.distribution_finder = distribution_finder

    def _execute(self, request: RecordRequest) -> RecordResponse:
        """Record the environment."""
        with self.uow:
            distributions = self.distribution_finder()
            request.trigger()
            computation_record = ComputationRecord(request.identifier, distributions)
            self.uow.records.add(computation_record)
            self.uow.commit()
        return self._response_cls()

    def __repr__(self) -> str:
        """Return a string representation of the record service."""
        return f"{self.__class__.__name__}(output_port={self.output_port!r}, repo={self.uow!r})"
