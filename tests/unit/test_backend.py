from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from compenv.adapters import DJAdapters
from compenv.backend import DJBackend, create_dj_backend
from compenv.infrastructure import DJInfrastructure, create_dj_infrastructure


@pytest.fixture
def dj_backend(fake_schema, fake_parent):
    return create_dj_backend(fake_schema, fake_parent.__name__)


def test_backend_is_created(dj_backend):
    assert isinstance(dj_backend, DJBackend)


def test_backend_is_dataclass(dj_backend):
    assert is_dataclass(dj_backend)


def test_uses_correct_infrastructure(dj_backend):
    assert isinstance(dj_backend.infra, DJInfrastructure)


def test_uses_correct_adapters(dj_backend):
    assert isinstance(dj_backend.adapters, DJAdapters)


def test_backend_is_frozen(dj_backend):
    with pytest.raises(FrozenInstanceError):
        dj_backend.adapters = "not adapters"
