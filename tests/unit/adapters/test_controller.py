from typing import List, Optional, Type

import pytest

from compenv.adapters.controller import DJController
from compenv.model.record import Identifier
from compenv.service.abstract import Response
from compenv.service.record import RecordRequest
from compenv.types import PrimaryKey

from ..conftest import FakeTranslator


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


class FakeService:
    request: RecordRequest

    @property
    def create_request(self) -> Type[RecordRequest]:
        return RecordRequest

    def __call__(self, request: RecordRequest) -> None:
        self.request = request


@pytest.fixture
def fake_service() -> FakeService:
    return FakeService()


@pytest.fixture
def controller(
    fake_service: FakeService,
    fake_translator: FakeTranslator,
) -> DJController:
    return DJController(fake_service, fake_translator)


def test_record_request_has_appropriate_identifier(
    controller: DJController, primary: PrimaryKey, fake_service: FakeService, identifier: Identifier
) -> None:
    controller.record(primary, lambda _: None)
    assert fake_service.request.identifier == identifier


class FakeMake:
    def __init__(self) -> None:
        self.primary_key: Optional[PrimaryKey] = None

    def __call__(self, primary_key: PrimaryKey) -> None:
        self.primary_key = primary_key


def test_record_request_has_appropriate_trigger(
    controller: DJController, primary: PrimaryKey, fake_service: FakeService
) -> None:
    fake_make = FakeMake()
    controller.record(primary, fake_make)
    fake_service.request.trigger()
    assert fake_make.primary_key == primary
