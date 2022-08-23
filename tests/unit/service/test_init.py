from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from compenv.service import initialize_services
from compenv.service.abstract import Request, Response, Service

from ..conftest import FakeRepository


def test_something() -> None:
    @dataclass(frozen=True)
    class FakeRequest(Request):
        message: str

    @dataclass(frozen=True)
    class FakeResponse(Response):
        message: str

    class FakeService(Service[FakeRequest, FakeResponse]):
        name = "fake_service"

        def __init__(self, *, output_port: Callable[[FakeResponse], None], repo: FakeRepository):
            self.output_port = output_port
            self.repo = repo

        def _execute(self, request: FakeRequest) -> FakeResponse:
            return FakeResponse(request.message)

    class FakeOutputPort:
        response: FakeResponse

        def __call__(self, response: FakeResponse) -> None:
            self.response = response

    services = {"fake_service": FakeService}
    fake_output_port = FakeOutputPort()
    output_ports = {"fake_service": fake_output_port}
    dependencies = {"repo": FakeRepository()}

    initialized_services = initialize_services(
        output_ports=output_ports, dependencies=dependencies, service_classes=services
    )  # type:  ignore
    initialized_services["fake_service"](FakeRequest("Pizza"))

    assert fake_output_port.response.message == "Pizza"
