from dataclasses import is_dataclass
from typing import Type

import pytest

from compenv.adapters import DJAdapters
from compenv.backend import DJBackend, create_dj_backend
from compenv.infrastructure import DJInfrastructure

from .conftest import FakeSchema, FakeTable


@pytest.fixture
def dj_backend(fake_schema: FakeSchema, fake_table: Type[FakeTable]) -> DJBackend:
    return create_dj_backend(fake_schema, fake_table.__name__)


def test_backend_is_created(dj_backend: DJBackend) -> None:
    assert isinstance(dj_backend, DJBackend)


def test_backend_is_dataclass(dj_backend: DJBackend) -> None:
    assert is_dataclass(dj_backend)


def test_uses_correct_infrastructure(dj_backend: DJBackend) -> None:
    assert isinstance(dj_backend.infra, DJInfrastructure)


def test_uses_correct_adapters(dj_backend: DJBackend) -> None:
    assert isinstance(dj_backend.adapters, DJAdapters)
