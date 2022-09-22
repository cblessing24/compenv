from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Type

import pytest
from datajoint.user_tables import Lookup, Part

from compenv.adapters.abstract import PartEntity
from compenv.adapters.entity import DJComputationRecord
from compenv.infrastructure.table import TableFacade, TableFactory

from ..conftest import FakeSchema, FakeTable

if TYPE_CHECKING:
    from datajoint.table import Entity


@pytest.fixture
def fake_tbl() -> FakeTable:
    class FakeRecordTable(FakeTable):
        attrs = {"a": int, "b": int}

        class Module(FakeTable):
            attrs = {"a": int, "b": int, "module_file": str, "module_is_active": str}

        class Distribution(FakeTable):
            attrs = {"a": int, "b": int, "distribution_name": str, "distribution_version": str}

        class Membership(FakeTable):
            attrs = {"a": int, "b": int, "module_file": str, "distribution_name": str, "distribution_version": str}

    return FakeRecordTable()


class FakeFactory:
    def __init__(self, table: FakeTable) -> None:
        self.table = table

    def __call__(self) -> FakeTable:
        return self.table

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


@pytest.fixture
def fake_factory(fake_tbl: FakeTable) -> FakeFactory:
    return FakeFactory(fake_tbl)


@pytest.fixture
def facade(fake_factory: FakeFactory) -> TableFacade:
    return TableFacade(fake_factory)


class TestInsert:
    @staticmethod
    def test_raises_error_if_record_already_exists(facade: TableFacade, dj_comp_rec: DJComputationRecord) -> None:
        facade.add(dj_comp_rec)
        with pytest.raises(ValueError, match="already exists!"):
            facade.add(dj_comp_rec)

    @staticmethod
    def test_inserts_master_entity_into_master_table(
        facade: TableFacade, dj_comp_rec: DJComputationRecord, fake_tbl: FakeTable
    ) -> None:
        facade.add(dj_comp_rec)
        assert fake_tbl.fetch1() == dj_comp_rec.primary

    @staticmethod
    @pytest.mark.parametrize("part,attr", list((p.__name__, p.master_attr) for p in DJComputationRecord.parts))
    def test_inserts_part_entities_into_part_tables(
        facade: TableFacade,
        primary: Entity,
        dj_comp_rec: DJComputationRecord,
        fake_tbl: FakeTable,
        part: str,
        attr: str,
    ) -> None:
        facade.add(dj_comp_rec)
        assert getattr(fake_tbl, part).fetch(as_dict=True) == [
            {**primary, **dataclasses.asdict(m)} for m in getattr(dj_comp_rec, attr)
        ]


def test_raises_error_if_record_does_not_exist(facade: TableFacade, primary: Entity) -> None:
    with pytest.raises(KeyError, match="does not exist!"):
        _ = facade.get(primary)


def test_fetches_dj_computation_record(facade: TableFacade, dj_comp_rec: DJComputationRecord) -> None:
    facade.add(dj_comp_rec)
    assert facade.get(dj_comp_rec.primary) == dj_comp_rec


def test_length(facade: TableFacade, dj_comp_rec: DJComputationRecord) -> None:
    facade.add(dj_comp_rec)
    assert len(facade) == 1


def test_iteration(facade: TableFacade, dj_comp_rec: DJComputationRecord, fake_tbl: FakeTable) -> None:
    facade.add(dj_comp_rec)
    assert list(iter(facade)) == list(iter(fake_tbl))


def test_facade_repr(facade: TableFacade) -> None:
    assert repr(facade) == "TableFacade(factory=FakeFactory())"


@pytest.fixture
def factory(fake_schema: FakeSchema, fake_table: Type[FakeTable]) -> TableFactory:
    return TableFactory(fake_schema, parent=fake_table.__name__)


@pytest.fixture
def produce_instance(factory: TableFactory) -> Lookup:
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
    _ = TableFactory(fake_schema, parent=fake_table.__name__)()
    assert fake_schema.context == {"foo": FakeTable, "FakeTable": fake_table}


def test_if_instance_is_instance_of_class(produce_instance: Lookup, fake_schema: FakeSchema) -> None:
    assert isinstance(produce_instance, fake_schema.decorated_tables["FakeTableRecord"])


def test_instance_is_cached(factory: TableFactory) -> None:
    assert factory() is factory()


def test_factory_repr(factory: TableFactory) -> None:
    assert repr(factory) == "TableFactory(schema=FakeSchema(), parent='FakeTable')"
