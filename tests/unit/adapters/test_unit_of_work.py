from __future__ import annotations

import pytest

from compenv.adapters.abstract import AbstractConnection, AbstractTransaction
from compenv.adapters.unit_of_work import DJUnitOfWork
from compenv.model.record import ComputationRecord, Identifier

from ..conftest import FakeRepository


class FakeConnection(AbstractConnection):
    def __init__(self, repository: FakeRepository) -> None:
        self.is_connected = False
        self._transaction = FakeTransaction(repository)

    @property
    def transaction(self) -> FakeTransaction:
        return self._transaction

    def open(self) -> None:
        self.is_connected = True

    def close(self) -> None:
        self.is_connected = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(repository={repr(self.transaction.repository)})"


class FakeTransaction(AbstractTransaction):
    def __init__(self, repository: FakeRepository) -> None:
        self.computation_records: dict[Identifier, ComputationRecord] = {}
        self.repository = repository
        self.in_transaction = False

    def start(self) -> None:
        self.computation_records = self.repository.comp_recs.copy()
        self.in_transaction = True

    def commit(self) -> None:
        self.in_transaction = False

    def rollback(self) -> None:
        if self.in_transaction:
            self.repository.comp_recs = self.computation_records
            self.in_transaction = False


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


def test_accessing_records_raises_runtime_error_outside_of_context(uow: DJUnitOfWork) -> None:
    with pytest.raises(RuntimeError, match="outside of context"):
        uow.records


def test_can_access_records_within_context(uow: DJUnitOfWork) -> None:
    with uow:
        uow.records


def test_accessing_records_after_exiting_context_raises_runtime_error(uow: DJUnitOfWork) -> None:
    with uow:
        pass
    with pytest.raises(RuntimeError, match="outside of context"):
        uow.records


def test_rolls_back_by_default(uow: DJUnitOfWork, computation_record: ComputationRecord) -> None:
    with uow:
        uow.records.add(computation_record)
    with uow:
        assert len(uow.records) == 0


def test_commit(
    uow: DJUnitOfWork,
    computation_record: ComputationRecord,
) -> None:
    with uow:
        uow.records.add(computation_record)
        uow.commit()
    with uow:
        assert len(uow.records) == 1


def test_repr(uow: DJUnitOfWork) -> None:
    assert repr(uow) == "DJUnitOfWork(connection=FakeConnection(repository=FakeRepository()), records=FakeRepository())"
