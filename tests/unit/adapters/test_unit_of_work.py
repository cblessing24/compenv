from __future__ import annotations

import pytest

from compenv.adapters.abstract import AbstractConnectionFacade
from compenv.adapters.unit_of_work import DJUnitOfWork
from compenv.model.record import ComputationRecord, Identifier

from ..conftest import FakeRepository


class FakeConnection(AbstractConnectionFacade):
    def __init__(self, repository: FakeRepository) -> None:
        self.repository = repository
        self.computation_records: dict[Identifier, ComputationRecord] = {}
        self.in_transaction = False
        self.is_connected = False

    def open(self) -> None:
        self.is_connected = True

    def start(self) -> None:
        self.computation_records = self.repository.comp_recs.copy()
        self.in_transaction = True

    def commit(self) -> None:
        self.in_transaction = False

    def rollback(self) -> None:
        if self.in_transaction:
            self.repository.comp_recs = self.computation_records
            self.in_transaction = False

    def close(self) -> None:
        self.is_connected = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(repository={repr(self.repository)})"


@pytest.fixture
def fake_connection(fake_repository: FakeRepository) -> FakeConnection:
    return FakeConnection(fake_repository)


@pytest.fixture
def uow(fake_connection: FakeConnection, fake_repository: FakeRepository) -> DJUnitOfWork:
    return DJUnitOfWork(fake_connection, fake_repository)


def test_opens_connection_on_entering_context(uow: DJUnitOfWork, fake_connection: FakeConnection) -> None:
    with uow:
        assert fake_connection.is_connected


def test_closes_connection_on_leaving_context(uow: DJUnitOfWork, fake_connection: FakeConnection) -> None:
    with uow:
        pass
    assert not fake_connection.is_connected


def test_rolls_back_by_default(uow: DJUnitOfWork, computation_record: ComputationRecord) -> None:
    with uow as uow:
        uow.records.add(computation_record)
    assert len(uow.records) == 0


def test_commit(
    uow: DJUnitOfWork,
    computation_record: ComputationRecord,
) -> None:
    with uow as uow:
        uow.records.add(computation_record)
        uow.commit()
    assert len(uow.records) == 1


def test_repr(uow: DJUnitOfWork) -> None:
    assert repr(uow) == "DJUnitOfWork(connection=FakeConnection(repository=FakeRepository()), records=FakeRepository())"
