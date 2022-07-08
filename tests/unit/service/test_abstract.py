import dataclasses

import pytest

from compenv.service.abstract import Request, Response, Service


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

    def __init__(self, repo, output_port, response):
        super().__init__(repo, output_port)
        self.requests = []
        self.response = response

    def _execute(self, request: MyRequest) -> MyResponse:
        self.requests.append(request)
        return self.response


@pytest.fixture
def my_request():
    return MyRequest(42, "foo")


@pytest.fixture
def my_response():
    return MyResponse(1337, "bar")


@pytest.fixture
def service(fake_output_port, my_response):
    return MyService("dummy_repo", output_port=fake_output_port, response=my_response)


def test_correct_request_gets_created(service, my_request):
    assert service.create_request(**dataclasses.asdict(my_request)) == my_request


def test_service_gets_executed_with_request(service, my_request):
    service(my_request)
    assert service.requests == [my_request]


def test_response_gets_passed_to_output_port(service, my_request, my_response, fake_output_port):
    service(my_request)
    assert fake_output_port.responses == [my_response]
