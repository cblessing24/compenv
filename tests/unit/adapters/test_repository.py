import pytest

from repro.adapters.repository import AbstractTableFacade, DJCompRecRepo, DJComputationRecord, DJModule
from repro.model.computation import ComputationRecord


@pytest.fixture
def identifier():
    return "identifier"


@pytest.fixture
def fake_translator(identifier, primary):
    class FakeTranslator:
        def __init__(self, identifier, primary):
            self._identifier = identifier
            self._primary = primary

        def to_identifier(self, primary):
            assert primary == self._primary
            return self._identifier

        def to_primary_key(self, identifier):
            assert identifier == self._identifier
            return self._primary

        def __repr__(self):
            return f"{self.__class__.__name__}()"

    return FakeTranslator(identifier, primary)


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


@pytest.fixture
def repo(fake_translator, fake_facade):
    return DJCompRecRepo(fake_translator, fake_facade)


@pytest.fixture
def comp_rec(identifier, record):
    return ComputationRecord(identifier, record)


@pytest.fixture
def add_computation_record(repo, identifier, comp_rec):
    repo[identifier] = comp_rec


@pytest.mark.usefixtures("add_computation_record")
class TestAdd:
    @staticmethod
    def test_raises_error_if_already_existing(repo, identifier, comp_rec):
        with pytest.raises(ValueError, match="already exists!"):
            repo[identifier] = comp_rec

    @staticmethod
    def test_inserts_dj_computation_record(fake_facade, primary, dj_comp_rec):
        assert fake_facade[primary] == dj_comp_rec


@pytest.mark.parametrize("method", ["__delitem__", "__getitem__"])
def test_raises_error_if_not_existing(repo, identifier, method):
    with pytest.raises(KeyError, match="does not exist!"):
        getattr(repo, method)(identifier)


def test_removes_computation_record(repo, identifier, comp_rec, fake_facade, primary):
    repo[identifier] = comp_rec
    del repo[identifier]
    with pytest.raises(KeyError):
        fake_facade[primary]


class TestGet:
    @staticmethod
    @pytest.mark.usefixtures("add_computation_record")
    def test_gets_computation_record_if_existing(repo, comp_rec, identifier):
        assert repo[identifier] == comp_rec

    @staticmethod
    def test_raises_error_if_missing_module_referenced_in_affiliation(
        primary, repo, identifier, fake_facade, dj_dists, dj_module_affiliations
    ):
        fake_facade[primary] = DJComputationRecord(
            modules=frozenset([DJModule(module_file="module1.py", module_is_active="False")]),
            distributions=dj_dists,
            module_affiliations=dj_module_affiliations,
        )
        with pytest.raises(ValueError, match="Module referenced in affiliation"):
            repo[identifier]


def test_iteration(repo, identifier, comp_rec):
    repo[identifier] = comp_rec
    assert list(iter(repo)) == [identifier]


def test_length(repo, identifier, comp_rec):
    repo[identifier] = comp_rec
    assert len(repo) == 1


def test_repr(repo):
    assert repr(repo) == "DJCompRecRepo(translator=FakeTranslator(), facade=FakeRecordTableFacade())"
