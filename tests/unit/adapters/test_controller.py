from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, List, Optional, Type, TypeVar

import pytest

from compenv.adapters.controller import DJController
from compenv.model.record import Identifier
from compenv.service.abstract import Request, Response
from compenv.service.diff import DiffRequest
from compenv.service.record import RecordRequest
from compenv.types import PrimaryKey

from ..conftest import FakeTranslatorFactory


class FakePresenter:
    def __init__(self) -> None:
        self.responses: List[Response] = []

    def record(self, response: Response) -> None:
        self.responses.append(response)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


@pytest.fixture
def fake_presenter() -> FakePresenter:
    return FakePresenter()


T = TypeVar("T", bound=Request)


class FakeService(Generic[T]):
    request: T
    request_cls: Type[T]

    @property
    def create_request(self) -> Type[T]:
        return self.request_cls

    def __call__(self, request: T) -> None:
        self.request = request


@pytest.fixture
def fake_record_service() -> FakeService[RecordRequest]:
    service: FakeService[RecordRequest] = FakeService()
    service.request_cls = RecordRequest
    return service


@pytest.fixture
def fake_diff_service() -> FakeService[DiffRequest]:
    service: FakeService[DiffRequest] = FakeService()
    service.request_cls = DiffRequest
    return service


@pytest.fixture
def fake_services(
    fake_record_service: FakeService[RecordRequest], fake_diff_service: FakeService[DiffRequest]
) -> dict[str, FakeService[Any]]:
    return {"record": fake_record_service, "diff": fake_diff_service}


@pytest.fixture
def controller(
    fake_services: dict[str, FakeService],  # type: ignore[type-arg]
    fake_translator_factory: FakeTranslatorFactory,
) -> DJController:
    return DJController(fake_services, fake_translator_factory())


def test_record_request_has_appropriate_identifier(
    controller: DJController,
    primary: PrimaryKey,
    fake_record_service: FakeService[RecordRequest],
    identifier: Identifier,
) -> None:
    controller.record(primary, lambda _: None)
    assert fake_record_service.request.identifier == identifier


class FakeMake:
    def __init__(self) -> None:
        self.primary_key: Optional[PrimaryKey] = None

    def __call__(self, primary_key: PrimaryKey) -> None:
        self.primary_key = primary_key


def test_record_request_has_appropriate_trigger(
    controller: DJController, primary: PrimaryKey, fake_record_service: FakeService[RecordRequest]
) -> None:
    fake_make = FakeMake()
    controller.record(primary, fake_make)
    fake_record_service.request.trigger()
    assert fake_make.primary_key == primary


def test_diff_request_has_appropriate_identifiers(
    fake_services: Mapping[str, FakeService[Any]], fake_translator_factory: FakeTranslatorFactory
) -> None:
    key1, key2 = {"a": 0}, {"a": 1}
    identifier1, identifier2 = Identifier("identifier1"), Identifier("identifier2")
    fake_translator = fake_translator_factory({identifier1: key1, identifier2: key2})
    controller = DJController(fake_services, fake_translator)
    controller.diff(key1, key2)
    assert fake_services["diff"].request == DiffRequest(identifier1, identifier2)
