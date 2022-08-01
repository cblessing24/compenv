from pathlib import Path
from typing import Any, Dict, FrozenSet, Iterator, MutableMapping, Optional, Protocol, Type, TypeVar, Union

import pytest

from compenv.adapters.entity import DJComputationRecord, DJDistribution, DJMembership, DJModule
from compenv.model import record as record_module
from compenv.model.computation import ComputationRecord, Identifier
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

Primary = Dict[str, Union[int, float, str]]


@pytest.fixture
def active_distributions() -> ActiveDistributions:
    return ActiveDistributions(
        {Distribution("dist2", "0.1.1", modules=Modules({Module(Path("module2.py"), is_active=True)}))}
    )


@pytest.fixture
def installed_distributions(active_distributions: ActiveDistributions) -> InstalledDistributions:
    return InstalledDistributions(
        {
            Distribution("dist1", "0.1.0", modules=Modules({Module(Path("module1.py"), is_active=False)})),
        }.union(active_distributions)
    )


@pytest.fixture
def active_modules() -> ActiveModules:
    return ActiveModules({Module(Path("module2.py"), is_active=True)})


@pytest.fixture
def prepare_environment(installed_distributions: InstalledDistributions, active_modules: ActiveModules) -> None:
    def fake_get_active_modules() -> ActiveModules:
        return active_modules

    def fake_get_installed_distributions() -> InstalledDistributions:
        return installed_distributions

    record_module.get_active_modules = fake_get_active_modules
    record_module.get_installed_distributions = fake_get_installed_distributions


@pytest.fixture
def record(installed_distributions: InstalledDistributions, active_modules: ActiveModules) -> Record:
    return Record(
        installed_distributions=installed_distributions,
        active_modules=active_modules,
    )


@pytest.fixture
def computation_record(record: Record) -> ComputationRecord:
    return ComputationRecord(Identifier("identifier"), record)


@pytest.fixture
def primary() -> Dict[str, int]:
    return {"a": 0, "b": 1}


@pytest.fixture
def dj_modules() -> FrozenSet[DJModule]:
    return frozenset(
        [
            DJModule(module_file="module1.py", module_is_active="False"),
            DJModule(module_file="module2.py", module_is_active="True"),
        ]
    )


@pytest.fixture
def dj_dists() -> FrozenSet[DJDistribution]:
    return frozenset(
        [
            DJDistribution(distribution_name="dist1", distribution_version="0.1.0"),
            DJDistribution(distribution_name="dist2", distribution_version="0.1.1"),
        ]
    )


@pytest.fixture
def dj_memberships() -> FrozenSet[DJMembership]:
    return frozenset(
        [
            DJMembership(module_file="module1.py", distribution_name="dist1", distribution_version="0.1.0"),
            DJMembership(module_file="module2.py", distribution_name="dist2", distribution_version="0.1.1"),
        ]
    )


@pytest.fixture
def dj_comp_rec(
    primary: Primary,
    dj_modules: FrozenSet[DJModule],
    dj_dists: FrozenSet[DJDistribution],
    dj_memberships: FrozenSet[DJMembership],
) -> DJComputationRecord:
    return DJComputationRecord(primary=primary, modules=dj_modules, distributions=dj_dists, memberships=dj_memberships)


class FakeTrigger:
    triggered = False
    change_environment = False

    def __call__(self) -> None:
        if self.change_environment:
            self._change_environment()
        self.triggered = True

    def _change_environment(self) -> None:
        def fake_get_active_modules() -> ActiveModules:
            return ActiveModules()

        record_module.get_active_modules = fake_get_active_modules

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


@pytest.fixture
def fake_trigger() -> FakeTrigger:
    return FakeTrigger()


class FakeRepository(Repository):
    def __init__(self) -> None:
        self.comp_recs: Dict[Identifier, ComputationRecord] = {}

    def add(self, comp_rec: ComputationRecord) -> None:
        self.comp_recs[comp_rec.identifier] = comp_rec

    def get(self, identifier: Identifier) -> ComputationRecord:
        return self.comp_recs[identifier]

    def __iter__(self) -> Iterator[Identifier]:
        return iter(self.comp_recs)

    def __len__(self) -> int:
        return len(self.comp_recs)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


@pytest.fixture
def fake_repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def identifier() -> Identifier:
    return Identifier("identifier")


class FakeTranslator:
    def __init__(self, identifier: Identifier, primary: Primary) -> None:
        self._identifier = identifier
        self._primary = primary

    def to_internal(self, primary: Primary) -> Identifier:
        assert primary == self._primary
        return self._identifier

    def to_external(self, identifier: Identifier) -> Primary:
        assert identifier == self._identifier
        return self._primary

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


@pytest.fixture
def fake_translator(identifier: Identifier, primary: Primary) -> FakeTranslator:
    return FakeTranslator(identifier, primary)


class FakeConnection:
    def __init__(self) -> None:
        self.in_transaction: Optional[bool] = None

    def cancel_transaction(self) -> None:
        self.in_transaction = False


@pytest.fixture
def fake_connection() -> FakeConnection:

    return FakeConnection()


class FakeParent:
    def make(self, key: Any) -> None:
        pass


@pytest.fixture
def fake_parent() -> Type[FakeParent]:
    return FakeParent


class Table(Protocol):
    database: str
    connection: FakeConnection


T = TypeVar("T", bound=Table)


class FakeSchema:
    schema_tables: Dict[str, Type[Table]] = {}

    def __init__(self, schema_name: str, connection: FakeConnection) -> None:
        self.database = schema_name
        self.connection = connection
        self.decorated_tables: Dict[str, Type[Table]] = {}
        self.context: Optional[Dict[str, Type[FakeParent]]] = None

    def __call__(self, table_cls: Type[T], context: Optional[Dict[str, Type[FakeParent]]] = None) -> Type[T]:
        if context:
            self.context = context
        self.decorated_tables[table_cls.__name__] = table_cls
        table_cls.database = self.database
        table_cls.connection = self.connection
        return table_cls

    def spawn_missing_classes(self, context: MutableMapping[str, Type[Table]]) -> None:
        context.update(self.schema_tables)

    def __repr__(self) -> str:
        return "FakeSchema()"


@pytest.fixture
def fake_schema(fake_connection: FakeConnection, fake_parent: Type[Table]) -> FakeSchema:
    FakeSchema.schema_tables[fake_parent.__name__] = fake_parent

    return FakeSchema("schema", fake_connection)
