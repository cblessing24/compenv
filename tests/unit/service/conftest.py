import dataclasses
from typing import Callable, List

from compenv.service.abstract import _T, _V, Request, Response, Service


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
