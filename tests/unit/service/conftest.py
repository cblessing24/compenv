import dataclasses
from typing import Callable, List

import pytest

from compenv.service.abstract import _T, _V, Request, Response, Service, UnitOfWork

from ..conftest import FakeRepository


@dataclasses.dataclass(frozen=True)
class FakeRequest(Request):
    message: str


@dataclasses.dataclass(frozen=True)
class FakeResponse(Response):
    message: str


class RequestTrackingService(Service[_T, _V]):
    def __init__(self, *, output_port: Callable[[_V], None]) -> None:
        super().__init__(output_port=output_port)
        self.requests: List[_T] = []

    def __call__(self, request: _T) -> None:
        self.requests.append(request)
        super().__call__(request)


class FakeService(RequestTrackingService[FakeRequest, FakeResponse]):
    name = "fake_service"

    _request_cls = FakeRequest
    _response_cls = FakeResponse

    def _execute(self, request: FakeRequest) -> FakeResponse:
        return self._response_cls(request.message)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, records: FakeRepository) -> None:
        super().__init__()
        self._records = records
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        ...


@pytest.fixture
def fake_uow(fake_repository: FakeRepository) -> FakeUnitOfWork:
    return FakeUnitOfWork(fake_repository)
