from typing import Iterator, List, Tuple

import pytest

from compenv.adapters.abstract import AbstractTableFacade
from compenv.adapters.entity import DJComputationRecord
from compenv.types import PrimaryKey


class FakeRecordTableFacade(AbstractTableFacade[DJComputationRecord]):
    def __init__(self) -> None:
        self.dj_comp_recs: List[Tuple[PrimaryKey, DJComputationRecord]] = []

    def add(self, dj_comp_rec: DJComputationRecord) -> None:
        if (dj_comp_rec.primary, dj_comp_rec) in self.dj_comp_recs:
            raise ValueError
        self.dj_comp_recs.append((dj_comp_rec.primary, dj_comp_rec))

    def get(self, primary: PrimaryKey) -> DJComputationRecord:
        try:
            return next(r for (p, r) in self.dj_comp_recs if p == primary)
        except StopIteration as error:
            raise KeyError from error

    def __iter__(self) -> Iterator[PrimaryKey]:
        return (p for (p, _) in self.dj_comp_recs)

    def __len__(self) -> int:
        return len(self.dj_comp_recs)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


@pytest.fixture
def fake_facade() -> FakeRecordTableFacade:
    return FakeRecordTableFacade()
