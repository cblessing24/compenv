from __future__ import annotations

from collections.abc import Callable

from compenv.service import initialize_services

from ..conftest import FakeOutputPort
from .conftest import FakeRequest, FakeResponse, FakeService


def test_service_is_correctly_initialized(fake_output_port: FakeOutputPort) -> None:
    class FakeServiceWithDependency(FakeService):
        def __init__(
            self,
            *,
            output_port: Callable[[FakeResponse], None],
            dependency: str,
        ) -> None:
            super().__init__(output_port=output_port)
            self.dependency = dependency

    services = {"fake_service": FakeServiceWithDependency}
    output_ports = {"fake_service": fake_output_port}
    dependencies = {"dependency": "oven"}

    initialized_services = initialize_services(
        output_ports=output_ports, dependencies=dependencies, service_classes=services
    )
    initialized_services["fake_service"](FakeRequest("pizza"))

    assert fake_output_port.responses[0] == FakeResponse("pizza")
    assert initialized_services["fake_service"].dependency == "oven"
