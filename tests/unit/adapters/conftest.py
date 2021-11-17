import pytest

from compenv.adapters.abstract import AbstractTableFacade
from compenv.adapters.entity import DJComputationRecord


@pytest.fixture
def fake_facade():
    class FakeRecordTableFacade(AbstractTableFacade[DJComputationRecord]):
        def __init__(self):
            self.dj_comp_recs = []

        def __setitem__(self, primary, entity):
            if (primary, entity) in self.dj_comp_recs:
                raise ValueError
            self.dj_comp_recs.append((primary, entity))

        def __delitem__(self, primary):
            try:
                del self.dj_comp_recs[next(i for i, (p, _) in enumerate(self.dj_comp_recs) if p == primary)]
            except StopIteration as error:
                raise KeyError from error

        def __getitem__(self, primary):
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
