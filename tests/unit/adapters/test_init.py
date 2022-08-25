from dataclasses import is_dataclass

import pytest

from compenv.adapters import DJAdapters, create_dj_adapters
from compenv.adapters.controller import DJController
from compenv.adapters.presenter import PrintingPresenter
from compenv.adapters.repository import DJRepository
from compenv.adapters.translator import DJTranslator

from .conftest import FakeRecordTableFacade


@pytest.fixture
def dj_adapters(fake_facade: FakeRecordTableFacade) -> DJAdapters:
    return create_dj_adapters(fake_facade)


def test_adapters_are_created(dj_adapters: DJAdapters) -> None:
    assert isinstance(dj_adapters, DJAdapters)


def test_adapters_is_dataclass(dj_adapters: DJAdapters) -> None:
    assert is_dataclass(dj_adapters)


def test_correct_translator_is_used(dj_adapters: DJAdapters) -> None:
    assert isinstance(dj_adapters.translator, DJTranslator)


def test_correct_presenter_is_used(dj_adapters: DJAdapters) -> None:
    assert isinstance(dj_adapters.presenter, PrintingPresenter)


def test_correct_repository_is_used(dj_adapters: DJAdapters) -> None:
    assert isinstance(dj_adapters.repo, DJRepository)


def test_repo_uses_correct_translator(dj_adapters: DJAdapters) -> None:
    assert dj_adapters.translator is dj_adapters.repo.translator


def test_repo_uses_correct_facade(fake_facade: FakeRecordTableFacade, dj_adapters: DJAdapters) -> None:
    assert dj_adapters.repo.facade is fake_facade


def test_correct_controller_is_used(dj_adapters: DJAdapters) -> None:
    assert isinstance(dj_adapters.controller, DJController)


def test_controller_uses_correct_translator(dj_adapters: DJAdapters) -> None:
    assert dj_adapters.controller.translator is dj_adapters.translator
