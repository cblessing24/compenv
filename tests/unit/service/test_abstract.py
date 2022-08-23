from __future__ import annotations

import dataclasses
from collections.abc import Mapping

import pytest

from compenv.service.abstract import Service

from ..conftest import FakeOutputPort
from .conftest import FakeRequest, FakeResponse, FakeService


@pytest.fixture
def service(fake_output_port: FakeOutputPort) -> FakeService:
    return FakeService(output_port=fake_output_port)


def test_correct_request_gets_created(service: FakeService) -> None:
    fake_request = FakeRequest("pizza")
    assert service.create_request(**dataclasses.asdict(fake_request)) == fake_request


def test_service_gets_executed_with_request(service: FakeService) -> None:
    fake_request = FakeRequest("pizza")
    service(fake_request)
    assert service.requests == [fake_request]


def test_response_gets_passed_to_output_port(service: FakeService, fake_output_port: FakeOutputPort) -> None:
    service(FakeRequest("pizza"))
    assert fake_output_port.responses[0] == FakeResponse("pizza")


def test_abstract_subclass_raises_no_error() -> None:
    type("MyService", (Service,), {})


@pytest.fixture
def class_attributes() -> dict[str, object]:
    return {name: ... for name in list(Service.__annotations__) + ["_execute"]}


@pytest.mark.parametrize("missing", Service.__annotations__)
def test_missing_class_variable_raises_error(missing: str, class_attributes: Mapping[str, object]) -> None:
    class_attributes = {name: attr for name, attr in class_attributes.items() if name != missing}
    with pytest.raises(RuntimeError):
        type("MyService", (Service,), class_attributes)
