from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from compenv.infrastructure import DJInfrastructure, create_dj_infrastructure
from compenv.infrastructure.facade import DJTableFacade
from compenv.infrastructure.factory import DJTableFactory


@pytest.fixture
def dj_infra(fake_schema, fake_parent):
    return create_dj_infrastructure(fake_schema, fake_parent.__name__)


def test_infrastructure_is_created(dj_infra):
    assert isinstance(dj_infra, DJInfrastructure)


def test_infrastructure_is_dataclass(dj_infra):
    assert is_dataclass(dj_infra)


def test_correct_factory_is_used(dj_infra):
    assert isinstance(dj_infra.factory, DJTableFactory)


def test_factory_uses_correct_schema(dj_infra, fake_schema):
    assert dj_infra.factory.schema is fake_schema


def test_factory_uses_correct_table_name(dj_infra, fake_parent):
    assert dj_infra.factory.parent == fake_parent.__name__


def test_correct_facade_is_used(dj_infra):
    assert isinstance(dj_infra.facade, DJTableFacade)


def test_facade_uses_correct_factory(dj_infra):
    assert dj_infra.facade.factory is dj_infra.factory


def test_infrastructure_is_frozen(dj_infra):
    with pytest.raises(FrozenInstanceError):
        dj_infra.factory = "not a factory"
