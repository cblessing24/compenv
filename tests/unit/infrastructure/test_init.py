from dataclasses import is_dataclass
from typing import Type

import pytest

from compenv.infrastructure import DJInfrastructure, create_dj_infrastructure
from compenv.infrastructure.table import TableFacade, TableFactory

from ..conftest import FakeSchema, FakeTable


@pytest.fixture
def dj_infra(fake_schema: FakeSchema, fake_table: Type[FakeTable]) -> DJInfrastructure:
    return create_dj_infrastructure(fake_schema, fake_table.__name__)


def test_infrastructure_is_created(dj_infra: DJInfrastructure) -> None:
    assert isinstance(dj_infra, DJInfrastructure)


def test_infrastructure_is_dataclass(dj_infra: DJInfrastructure) -> None:
    assert is_dataclass(dj_infra)


def test_correct_factory_is_used(dj_infra: DJInfrastructure) -> None:
    assert isinstance(dj_infra.factory, TableFactory)


def test_factory_uses_correct_schema(dj_infra: DJInfrastructure, fake_schema: FakeSchema) -> None:
    assert dj_infra.factory.schema is fake_schema


def test_factory_uses_correct_table_name(dj_infra: DJInfrastructure, fake_table: Type[FakeTable]) -> None:
    assert dj_infra.factory.parent == fake_table.__name__


def test_correct_facade_is_used(dj_infra: DJInfrastructure) -> None:
    assert isinstance(dj_infra.facade, TableFacade)


def test_facade_uses_correct_factory(dj_infra: DJInfrastructure) -> None:
    assert dj_infra.facade.factory is dj_infra.factory
