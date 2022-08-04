from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import pytest

from compenv.adapters.entity import DJComputationRecord
from compenv.infrastructure.facade import DJTableFacade

from ..conftest import FakeTable

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
def facade(fake_factory: FakeFactory) -> DJTableFacade:
    return DJTableFacade(fake_factory)


class TestInsert:
    @staticmethod
    def test_raises_error_if_record_already_exists(facade: DJTableFacade, dj_comp_rec: DJComputationRecord) -> None:
        facade.add(dj_comp_rec)
        with pytest.raises(ValueError, match="already exists!"):
            facade.add(dj_comp_rec)

    @staticmethod
    def test_inserts_master_entity_into_master_table(
        facade: DJTableFacade, dj_comp_rec: DJComputationRecord, fake_tbl: FakeTable
    ) -> None:
        facade.add(dj_comp_rec)
        assert fake_tbl.fetch1() == dj_comp_rec.primary

    @staticmethod
    @pytest.mark.parametrize("part,attr", list((p.__name__, p.master_attr) for p in DJComputationRecord.parts))
    def test_inserts_part_entities_into_part_tables(
        facade: DJTableFacade,
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


def test_raises_error_if_record_does_not_exist(facade: DJTableFacade, primary: Entity) -> None:
    with pytest.raises(KeyError, match="does not exist!"):
        _ = facade.get(primary)


def test_fetches_dj_computation_record(facade: DJTableFacade, dj_comp_rec: DJComputationRecord) -> None:
    facade.add(dj_comp_rec)
    assert facade.get(dj_comp_rec.primary) == dj_comp_rec


def test_length(facade: DJTableFacade, dj_comp_rec: DJComputationRecord) -> None:
    facade.add(dj_comp_rec)
    assert len(facade) == 1


def test_iteration(facade: DJTableFacade, dj_comp_rec: DJComputationRecord, fake_tbl: FakeTable) -> None:
    facade.add(dj_comp_rec)
    assert list(iter(facade)) == list(iter(fake_tbl))


def test_repr(facade: DJTableFacade) -> None:
    assert repr(facade) == "DJTableFacade(factory=FakeFactory())"
