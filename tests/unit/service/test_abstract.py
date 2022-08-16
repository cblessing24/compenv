import dataclasses
from typing import Callable, List

import pytest

from compenv.service.abstract import Request, Response, Service

from ..conftest import FakeOutputPort


@dataclasses.dataclass(frozen=True)
class MyRequest(Request):
    my_param: int
    my_other_param: str


@dataclasses.dataclass(frozen=True)
class MyResponse(Response):
    my_response: int
    my_other_response: str


class MyService(Service[MyRequest, MyResponse]):
    _request_cls = MyRequest
    _response_cls = MyResponse

    def __init__(self, *, output_port: Callable[[MyResponse], None], response: MyResponse) -> None:
        super().__init__(output_port=output_port)
        self.requests: List[MyRequest] = []
        self.response = response

    def _execute(self, request: MyRequest) -> MyResponse:
        self.requests.append(request)
        return self.response


@pytest.fixture
def my_request() -> MyRequest:
    return MyRequest(42, "foo")


@pytest.fixture
def my_response() -> MyResponse:
    return MyResponse(1337, "bar")


@pytest.fixture
def service(fake_output_port: FakeOutputPort, my_response: MyResponse) -> MyService:
    return MyService(output_port=fake_output_port, response=my_response)


def test_correct_request_gets_created(service: MyService, my_request: MyRequest) -> None:
    assert service.create_request(**dataclasses.asdict(my_request)) == my_request


def test_service_gets_executed_with_request(service: MyService, my_request: MyRequest) -> None:
    service(my_request)
    assert service.requests == [my_request]


def test_response_gets_passed_to_output_port(
    service: MyService, my_request: MyRequest, my_response: MyResponse, fake_output_port: FakeOutputPort
) -> None:
    service(my_request)
    assert fake_output_port.responses == [my_response]
