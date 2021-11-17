from pathlib import Path

import pytest

from compenv.adapters.repository import DJComputationRecord, DJDistribution, DJMembership, DJModule
from compenv.model import record as record_module
from compenv.model.computation import ComputationRecord
from compenv.model.record import (
    ActiveDistributions,
    ActiveModules,
    Distribution,
    InstalledDistributions,
    Module,
    Modules,
    Record,
)
from compenv.service.abstract import Repository


@pytest.fixture
def active_distributions():
    return ActiveDistributions(
        {Distribution("dist2", "0.1.1", modules=Modules({Module(Path("module2.py"), is_active=True)}))}
    )


@pytest.fixture
def installed_distributions(active_distributions):
    return InstalledDistributions(
        {
            Distribution("dist1", "0.1.0", modules=Modules({Module(Path("module1.py"), is_active=False)})),
        }.union(active_distributions)
    )


@pytest.fixture
def active_modules():
    return ActiveModules({Module(Path("module2.py"), is_active=True)})


@pytest.fixture
def prepare_environment(installed_distributions, active_modules):
    def fake_get_active_modules():
        return iter(active_modules)

    def fake_get_installed_distributions():
        return iter(installed_distributions)

    record_module.get_active_modules = fake_get_active_modules
    record_module.get_installed_distributions = fake_get_installed_distributions


@pytest.fixture
def record(installed_distributions, active_modules):
    return Record(
        installed_distributions=installed_distributions,
        active_modules=active_modules,
    )


@pytest.fixture
def computation_record(record):
    return ComputationRecord("identifier", record)


@pytest.fixture
def primary():
    return {"a": 0, "b": 1}


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
def dj_memberships():
    return frozenset(
        [
            DJMembership(module_file="module1.py", distribution_name="dist1", distribution_version="0.1.0"),
            DJMembership(module_file="module2.py", distribution_name="dist2", distribution_version="0.1.1"),
        ]
    )


@pytest.fixture
def dj_comp_rec(dj_modules, dj_dists, dj_memberships):
    return DJComputationRecord(modules=dj_modules, distributions=dj_dists, memberships=dj_memberships)


@pytest.fixture
def fake_trigger():
    class FakeTrigger:
        triggered = False
        change_environment = False

        def __call__(self):
            if self.change_environment:
                self._change_environment()
            self.triggered = True

        def _change_environment(self):
            def fake_get_active_modules():
                return iter(frozenset())

            record_module.get_active_modules = fake_get_active_modules

        def __repr__(self):
            return f"{self.__class__.__name__}()"

    return FakeTrigger()


@pytest.fixture
def fake_repository():
    class FakeRepository(dict, Repository):
        def __repr__(self):
            return self.__class__.__name__ + "()"

    return FakeRepository()


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

        def to_primary(self, identifier):
            assert identifier == self._identifier
            return self._primary

        def __repr__(self):
            return f"{self.__class__.__name__}()"

    return FakeTranslator(identifier, primary)


@pytest.fixture
def fake_connection():
    class FakeConnection:
        def __init__(self):
            self.in_transaction = None

        def cancel_transaction(self):
            self.in_transaction = False

    return FakeConnection()


@pytest.fixture
def fake_parent():
    class FakeParent:
        def make(self, key):
            pass

    return FakeParent


@pytest.fixture
def fake_schema(fake_connection, fake_parent):
    class FakeSchema:
        schema_tables = {}

        def __init__(self, schema_name, connection):
            self.database = schema_name
            self.connection = connection
            self.decorated_tables = {}
            self.context = None

        def __call__(self, table_cls, context=None):
            if context:
                self.context = context
            self.decorated_tables[table_cls.__name__] = table_cls
            table_cls.database = self.database
            table_cls.connection = self.connection
            return table_cls

        def spawn_missing_classes(self, context):
            context.update(self.schema_tables)

        def __repr__(self):
            return "FakeSchema()"

    FakeSchema.schema_tables[fake_parent.__name__] = fake_parent

    return FakeSchema("schema", fake_connection)
