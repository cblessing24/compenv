from typing import Any, List, Mapping

import pytest

from compenv.adapters.controller import DJController
from compenv.model.computation import Identifier
from compenv.service.abstract import Response
from compenv.types import PrimaryKey
from tests.unit.conftest import FakeRepository, FakeTranslator


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


@pytest.fixture
def controller(
    fake_repository: FakeRepository, fake_translator: FakeTranslator, fake_presenter: FakePresenter
) -> DJController:
    return DJController(fake_repository, fake_translator, fake_presenter)


class FakeMake:
    def __init__(self) -> None:
        self.calls: List[Mapping[str, Any]] = []

    def __call__(self, key: Mapping[str, Any]) -> None:
        self.calls.append(key)


@pytest.fixture
def fake_make() -> FakeMake:
    return FakeMake()


def test_calling_record_calls_make_method_with_appropriate_key(
    controller: DJController, primary: PrimaryKey, fake_make: FakeMake
) -> None:
    controller.record(primary, fake_make)
    assert fake_make.calls == [primary]


def test_calling_record_inserts_record_with_appropriate_identifier(
    controller: DJController,
    primary: PrimaryKey,
    fake_make: FakeMake,
    fake_repository: FakeRepository,
    identifier: Identifier,
) -> None:
    controller.record(primary, fake_make)
    assert list(fake_repository) == [identifier]


def test_repr(controller: DJController) -> None:
    assert (
        repr(controller)
        == "DJController(repo=FakeRepository(), translator=FakeTranslator(), presenter=FakePresenter())"
    )
