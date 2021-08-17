import pytest

from repro.adapters.repository import (
    AbstractDJRecTable,
    DJCompRecRepo,
    DJComputationRecord,
    DJDistribution,
    DJModule,
    DJModuleAffiliation,
)
from repro.model.computation import ComputationRecord


@pytest.fixture
def identifier():
    return "identifier"


@pytest.fixture
def primary():
    return {"a": 0, "b": 1}


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
def fake_record_table():
    class FakeRecTable(AbstractDJRecTable):
        def __init__(self):
            self.dj_comp_recs = []

        def insert(self, dj_comp_rec):
            if dj_comp_rec in self.dj_comp_recs:
                raise ValueError
            self.dj_comp_recs.append(dj_comp_rec)

        def delete(self, primary):
            try:
                del self.dj_comp_recs[next(i for i, r in enumerate(self.dj_comp_recs) if r.primary == primary)]
            except StopIteration as error:
                raise KeyError from error

        def fetch(self, primary):
            try:
                return next(r for r in self.dj_comp_recs if r.primary == primary)
            except StopIteration as error:
                raise KeyError from error

        def __repr__(self):
            return self.__class__.__name__ + "()"

    return FakeRecTable()


@pytest.fixture
def repo(fake_translator, fake_record_table):
    return DJCompRecRepo(fake_translator, fake_record_table)


@pytest.fixture
def dj_modules():
    return frozenset(
        [
            DJModule(module_file="module1.py", module_is_active="False"),
            DJModule(module_file="module2.py", module_is_active="True"),
        ]
    )


@pytest.fixture
def dj_dists():
    return frozenset(
        [
            DJDistribution(distribution_name="dist1", distribution_version="0.1.0"),
            DJDistribution(distribution_name="dist2", distribution_version="0.1.1"),
        ]
    )


@pytest.fixture
def dj_module_affiliations():
    return frozenset(
        [
            DJModuleAffiliation(module_file="module1.py", distribution_name="dist1"),
            DJModuleAffiliation(module_file="module2.py", distribution_name="dist2"),
        ]
    )


@pytest.fixture
def computation_record(identifier, record):
    return ComputationRecord(identifier, record)


@pytest.fixture
def dj_comp_rec(primary, dj_modules, dj_dists, dj_module_affiliations):
    return DJComputationRecord(
        primary=primary, modules=dj_modules, distributions=dj_dists, module_affiliations=dj_module_affiliations
    )


@pytest.fixture
def add_computation_record(repo, computation_record):
    repo.add(computation_record)


@pytest.mark.usefixtures("add_computation_record")
class TestAdd:
    @staticmethod
    def test_raises_error_if_already_existing(repo, computation_record):
        with pytest.raises(ValueError, match="already exists!"):
            repo.add(computation_record)

    @staticmethod
    def test_inserts_dj_computation_record(fake_record_table, primary, dj_comp_rec):
        assert fake_record_table.fetch(primary) == dj_comp_rec


@pytest.mark.parametrize("method", ["remove", "get"])
def test_raises_error_if_not_existing(repo, identifier, method):
    with pytest.raises(KeyError, match="does not exist!"):
        getattr(repo, method)(identifier)


def test_removes_computation_record(repo, computation_record, identifier, fake_record_table, primary):
    repo.add(computation_record)
    repo.remove(identifier)
    with pytest.raises(KeyError):
        fake_record_table.fetch(primary)


class TestGet:
    @staticmethod
    @pytest.mark.usefixtures("add_computation_record")
    def test_gets_computation_record_if_existing(repo, computation_record, identifier):
        assert repo.get(identifier) == computation_record

    @staticmethod
    def test_raises_error_if_missing_module_referenced_in_affiliation(
        primary, repo, identifier, fake_record_table, dj_dists, dj_module_affiliations
    ):
        fake_record_table.insert(
            DJComputationRecord(
                primary=primary,
                modules=frozenset([DJModule(module_file="module1.py", module_is_active="False")]),
                distributions=dj_dists,
                module_affiliations=dj_module_affiliations,
            )
        )
        with pytest.raises(ValueError, match="Module referenced in affiliation"):
            repo.get(identifier)


def test_repr(repo):
    assert repr(repo) == "DJCompRecRepo(translator=FakeTranslator(), rec_table=FakeRecTable())"
