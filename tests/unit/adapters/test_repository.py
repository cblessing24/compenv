import pytest

from compenv.adapters.entity import DJComputationRecord, DJModule
from compenv.adapters.repository import DJRepository
from compenv.model.computation import ComputationRecord


@pytest.fixture
def repo(fake_translator, fake_facade):
    return DJRepository(fake_translator, fake_facade)


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
    def test_raises_error_if_missing_module_referenced_in_membership(
        primary, repo, identifier, fake_facade, dj_dists, dj_memberships
    ):
        fake_facade[primary] = DJComputationRecord(
            modules=frozenset([DJModule(module_file="module1.py", module_is_active="False")]),
            distributions=dj_dists,
            memberships=dj_memberships,
        )
        with pytest.raises(ValueError, match="Module referenced in membership"):
            repo[identifier]


def test_iteration(repo, identifier, comp_rec):
    repo[identifier] = comp_rec
    assert list(iter(repo)) == [identifier]


def test_length(repo, identifier, comp_rec):
    repo[identifier] = comp_rec
    assert len(repo) == 1


def test_repr(repo):
    assert repr(repo) == "DJRepository(translator=FakeTranslator(), facade=FakeRecordTableFacade())"
