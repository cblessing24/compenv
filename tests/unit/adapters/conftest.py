import pytest

from compenv.adapters.abstract import AbstractTableFacade
from compenv.adapters.entity import DJComputationRecord


@pytest.fixture
def fake_facade():
    class FakeRecordTableFacade(AbstractTableFacade[DJComputationRecord]):
        def __init__(self):
            self.dj_comp_recs = []

        def add(self, master_entity):
            if (master_entity.primary, master_entity) in self.dj_comp_recs:
                raise ValueError
            self.dj_comp_recs.append((master_entity.primary, master_entity))

        def get(self, primary):
            try:
                return next(r for (p, r) in self.dj_comp_recs if p == primary)
            except StopIteration as error:
                raise KeyError from error

        def __iter__(self):
            return (p for (p, _) in self.dj_comp_recs)

        def __len__(self):
            return len(self.dj_comp_recs)

        def __repr__(self):
            return self.__class__.__name__ + "()"

    return FakeRecordTableFacade()
