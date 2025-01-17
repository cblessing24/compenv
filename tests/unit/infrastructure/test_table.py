from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Type

import pytest
from datajoint.user_tables import Lookup, Part

from compenv.adapters.abstract import PartEntity
from compenv.adapters.entity import DJComputationRecord
from compenv.infrastructure.table import Table, TableFactory

from ..conftest import FakeSchema, FakeTable

if TYPE_CHECKING:
    from datajoint.table import Entity


class FakeFactory:
    def __init__(self, table: FakeTable) -> None:
        self.table = table

    def __call__(self) -> FakeTable:
        return self.table

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


class TestTable:
    @staticmethod
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

    @staticmethod
    @pytest.fixture
    def fake_factory(fake_tbl: FakeTable) -> FakeFactory:
        return FakeFactory(fake_tbl)

    @staticmethod
    @pytest.fixture
    def table(fake_factory: FakeFactory) -> Table:
        return Table(fake_factory)

    @staticmethod
    def test_insert_raises_error_if_record_already_exists(table: Table, dj_comp_rec: DJComputationRecord) -> None:
        table.add(dj_comp_rec)
        with pytest.raises(ValueError, match="already exists!"):
            table.add(dj_comp_rec)

    @staticmethod
    def test_inserts_master_entity_into_master_table(
        table: Table, dj_comp_rec: DJComputationRecord, fake_tbl: FakeTable
    ) -> None:
        table.add(dj_comp_rec)
        assert fake_tbl.fetch1() == dj_comp_rec.primary

    @staticmethod
    @pytest.mark.parametrize("part,attr", list((p.__name__, p.master_attr) for p in DJComputationRecord.parts))
    def test_inserts_part_entities_into_part_tables(
        table: Table,
        primary: Entity,
        dj_comp_rec: DJComputationRecord,
        fake_tbl: FakeTable,
        part: str,
        attr: str,
    ) -> None:
        table.add(dj_comp_rec)
        assert getattr(fake_tbl, part).fetch(as_dict=True) == [
            {**primary, **dataclasses.asdict(m)} for m in getattr(dj_comp_rec, attr)
        ]

    @staticmethod
    def test_get_raises_error_if_record_does_not_exist(table: Table, primary: Entity) -> None:
        with pytest.raises(KeyError, match="does not exist!"):
            _ = table.get(primary)

    @staticmethod
    def test_get_dj_computation_record(table: Table, dj_comp_rec: DJComputationRecord) -> None:
        table.add(dj_comp_rec)
        assert table.get(dj_comp_rec.primary) == dj_comp_rec

    @staticmethod
    def test_length(table: Table, dj_comp_rec: DJComputationRecord) -> None:
        table.add(dj_comp_rec)
        assert len(table) == 1

    @staticmethod
    def test_iteration(table: Table, dj_comp_rec: DJComputationRecord, fake_tbl: FakeTable) -> None:
        table.add(dj_comp_rec)
        assert list(iter(table)) == list(iter(fake_tbl))

    @staticmethod
    def test_repr(table: Table) -> None:
        assert repr(table) == "Table(factory=FakeFactory())"


class FakeSchemaFactory:
    def __init__(self, fake_schema: FakeSchema) -> None:
        self.fake_schema = fake_schema

    def __call__(self) -> FakeSchema:
        return self.fake_schema

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(fake_schema={repr(self.fake_schema)})"


@pytest.fixture
def fake_schema_factory(fake_schema: FakeSchema) -> FakeSchemaFactory:
    return FakeSchemaFactory(fake_schema)


@pytest.fixture
def factory(fake_schema_factory: FakeSchemaFactory, fake_table: Type[FakeTable]) -> TableFactory:
    return TableFactory(fake_schema_factory, parent=fake_table.__name__)


@pytest.fixture
def produce_instance(factory: TableFactory) -> Lookup:
    return factory()


class TestFactory:
    @staticmethod
    def test_parent_is_added_to_context_when_schema_is_called(
        fake_schema_factory: FakeSchemaFactory, fake_schema: FakeSchema, fake_table: Type[FakeTable]
    ) -> None:
        fake_schema.context = {"foo": FakeTable}
        _ = TableFactory(fake_schema_factory, parent=fake_table.__name__)()
        assert fake_schema.context == {"foo": FakeTable, "FakeTable": fake_table}

    @staticmethod
    def test_if_instance_is_instance_of_class(produce_instance: Lookup, fake_schema: FakeSchema) -> None:
        assert isinstance(produce_instance, fake_schema.decorated_tables["FakeTableRecord"])

    @staticmethod
    def test_repr(factory: TableFactory) -> None:
        assert (
            repr(factory)
            == "TableFactory(schema_factory=FakeSchemaFactory(fake_schema=FakeSchema()), parent='FakeTable')"
        )


@staticmethod
@pytest.mark.usefixtures("produce_instance")
class TestFactoryMasterClass:
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
class TestFactoryPartClasses:
    @staticmethod
    def test_part_classes_are_present_on_table_class(fake_schema: FakeSchema, part: Type[PartEntity]) -> None:
        assert hasattr(fake_schema.decorated_tables["FakeTableRecord"], part.__name__)

    @staticmethod
    def test_part_classes_are_subclass_of_part_table(fake_schema: FakeSchema, part: Type[PartEntity]) -> None:
        assert issubclass(getattr(fake_schema.decorated_tables["FakeTableRecord"], part.__name__), Part)

    @staticmethod
    def test_part_classes_have_correct_definitions(fake_schema: FakeSchema, part: Type[PartEntity]) -> None:
        assert getattr(fake_schema.decorated_tables["FakeTableRecord"], part.__name__).definition == part.definition
