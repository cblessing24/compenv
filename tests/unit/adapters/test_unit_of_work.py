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
        self._in_transaction = False

    def open(self) -> None:
        pass

    def start(self) -> None:
        if self._in_transaction:
            raise RuntimeError("Nested transactions are not allowed")
        self.computation_records = self.repository.comp_recs.copy()
        self._in_transaction = True

    def commit(self) -> None:
        self._in_transaction = False

    def rollback(self) -> None:
        if self._in_transaction:
            self.repository.comp_recs = self.computation_records
            self._in_transaction = False

    @property
    def in_transaction(self) -> bool:
        return self._in_transaction

    def close(self) -> None:
        pass


@pytest.fixture
def fake_connection(fake_repository: FakeRepository) -> FakeConnection:
    return FakeConnection(fake_repository)


def test_rolls_back_by_default(
    fake_connection: FakeConnection, fake_repository: FakeRepository, computation_record: ComputationRecord
) -> None:
    with DJUnitOfWork(fake_connection, fake_repository) as uow:
        uow.records.add(computation_record)
    assert len(uow.records) == 0


def test_no_nested_transactions(
    fake_connection: FakeConnection, fake_repository: FakeRepository, computation_record: ComputationRecord
) -> None:
    fake_connection.start()
    with DJUnitOfWork(fake_connection, fake_repository) as uow:
        uow.records.add(computation_record)


def test_commit(
    fake_connection: FakeConnection, fake_repository: FakeRepository, computation_record: ComputationRecord
) -> None:
    with DJUnitOfWork(fake_connection, fake_repository) as uow:
        uow.records.add(computation_record)
        uow.commit()
    assert len(uow.records) == 1
