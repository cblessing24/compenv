from typing import Type

import pytest
from datajoint.user_tables import Lookup, Part

from compenv.adapters.abstract import PartEntity
from compenv.infrastructure.factory import DJTableFactory

from ..conftest import FakeSchema, FakeTable


@pytest.fixture
def factory(fake_schema: FakeSchema, fake_table: Type[FakeTable]) -> DJTableFactory:
    return DJTableFactory(fake_schema, parent=fake_table.__name__)


@pytest.fixture
def produce_instance(factory: DJTableFactory) -> Lookup:
    return factory()


@pytest.mark.usefixtures("produce_instance")
class TestMasterClass:
    @staticmethod
    def test_class_has_correct_name(fake_schema: FakeSchema) -> None:
        assert "FakeTableRecord" in fake_schema.decorated_tables

    @staticmethod
    def test_class_is_lookup_table(fake_schema: FakeSchema) -> None:
        assert issubclass(fake_schema.decorated_tables["FakeTableRecord"], Lookup)

    @staticmethod
    def test_class_has_correct_definition(fake_schema: FakeSchema) -> None:
        assert fake_schema.decorated_tables["FakeTableRecord"].definition == "-> FakeTable"


@pytest.mark.parametrize("part", PartEntity.__subclasses__())
@pytest.mark.usefixtures("produce_instance")
class TestPartClasses:
    @staticmethod
    def test_part_classes_are_present_on_table_class(fake_schema: FakeSchema, part: Type[PartEntity]) -> None:
        assert hasattr(fake_schema.decorated_tables["FakeTableRecord"], part.__name__)

    @staticmethod
    def test_part_classes_are_subclass_of_part_table(fake_schema: FakeSchema, part: Type[PartEntity]) -> None:
        assert issubclass(getattr(fake_schema.decorated_tables["FakeTableRecord"], part.__name__), Part)

    @staticmethod
    def test_part_classes_have_correct_definitions(fake_schema: FakeSchema, part: Type[PartEntity]) -> None:
        assert getattr(fake_schema.decorated_tables["FakeTableRecord"], part.__name__).definition == part.definition


def test_parent_is_added_to_context_when_schema_is_called(fake_schema: FakeSchema, fake_table: Type[FakeTable]) -> None:
    fake_schema.context = {"foo": FakeTable}
    _ = DJTableFactory(fake_schema, parent=fake_table.__name__)()
    assert fake_schema.context == {"foo": FakeTable, "FakeTable": fake_table}


def test_if_instance_is_instance_of_class(produce_instance: Lookup, fake_schema: FakeSchema) -> None:
    assert isinstance(produce_instance, fake_schema.decorated_tables["FakeTableRecord"])


def test_instance_is_cached(factory: DJTableFactory) -> None:
    assert factory() is factory()


def test_repr(factory: DJTableFactory) -> None:
    assert repr(factory) == "DJTableFactory(schema=FakeSchema(), parent='FakeTable')"
