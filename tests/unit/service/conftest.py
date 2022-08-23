import dataclasses
from typing import Callable, List

from compenv.service.abstract import Request, Response, Service


@dataclasses.dataclass(frozen=True)
class FakeRequest(Request):
    message: str


@dataclasses.dataclass(frozen=True)
class FakeResponse(Response):
    message: str


class FakeService(Service[FakeRequest, FakeResponse]):
    name = "fake_service"

    _request_cls = FakeRequest
    _response_cls = FakeResponse

    def __init__(self, *, output_port: Callable[[FakeResponse], None]) -> None:
        super().__init__(output_port=output_port)
        self.requests: List[FakeRequest] = []

    def _execute(self, request: FakeRequest) -> FakeResponse:
        self.requests.append(request)
        return self._response_cls(request.message)
