from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    FrozenSet,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

import pytest
from datajoint.errors import DuplicateError

from compenv.adapters.entity import DJComputationRecord, DJDistribution, DJMembership, DJModule
from compenv.infrastructure.types import Connection, Table
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
from compenv.types import PrimaryKey

if TYPE_CHECKING:
    from datajoint.table import Entity


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
    primary: PrimaryKey,
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
        def fake_get_installed_distributions() -> InstalledDistributions:
            return InstalledDistributions()

        record_module.get_installed_distributions = fake_get_installed_distributions

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
    def __init__(self, identifier: Identifier, primary: PrimaryKey) -> None:
        self._identifier = identifier
        self._primary = primary

    def to_internal(self, primary: PrimaryKey) -> Identifier:
        assert primary == self._primary
        return self._identifier

    def to_external(self, identifier: Identifier) -> PrimaryKey:
        assert identifier == self._identifier
        return self._primary

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


@pytest.fixture
def fake_translator(identifier: Identifier, primary: PrimaryKey) -> FakeTranslator:
    return FakeTranslator(identifier, primary)


class FakeConnection:
    def __init__(self) -> None:
        self.in_transaction: Optional[bool] = None

    def cancel_transaction(self) -> None:
        self.in_transaction = False


@pytest.fixture
def fake_connection() -> FakeConnection:

    return FakeConnection()


class FakeTable:
    attrs: ClassVar[Mapping[str, Union[Type[int], Type[str]]]]
    connection: Connection
    database: str
    definition: str
    _data: ClassVar[list[Entity]]
    _restriction: ClassVar[Entity]

    @classmethod
    def _restricted_data(cls) -> list[Entity]:
        if not cls._restriction:
            return cls._data
        return [d for d in cls._data if all(i in d.items() for i in cls._restriction.items())]

    @classmethod
    def insert(cls, entities: Iterator[Entity]) -> None:
        for entity in entities:
            cls.insert1(entity)

    @classmethod
    def insert1(cls, entity: Entity) -> None:
        cls._check_attr_names(entity)

        for attr_name, attr_value in entity.items():
            if not isinstance(attr_value, cls.attrs[attr_name]):
                raise ValueError(
                    f"Expected instance of type '{cls.attrs[attr_name]}' "
                    f"for attribute with name {attr_name}, got '{type(attr_value)}'!"
                )

        if entity in cls._data:
            raise DuplicateError

        cls._data.append(dict(entity))

    @classmethod
    def delete_quick(cls) -> None:
        for entity in cls._restricted_data():
            del cls._data[cls._data.index(entity)]

    @classmethod
    def fetch(cls, as_dict: bool = False) -> list[Entity]:
        if as_dict is not True:
            raise ValueError("'as_dict' must be set to 'True' when fetching!")
        return cls._restricted_data()

    @classmethod
    def fetch1(cls) -> Entity:
        if len(cls._restricted_data()) != 1:
            raise RuntimeError("Can't fetch zero or more than one entity!")

        return cls._restricted_data()[0]

    @classmethod
    def __and__(cls, restriction: Entity) -> Type[FakeTable]:
        cls._check_attr_names(restriction)
        cls._restriction = dict(restriction)
        return cls

    @classmethod
    def __contains__(cls, item: object) -> bool:
        return item in cls._restricted_data()

    @classmethod
    def __eq__(cls, other: object) -> bool:
        if not isinstance(other, list):
            raise TypeError(f"Expected other to be of type dict, got {type(other)}!")

        return all(e in cls._data for e in other)

    @classmethod
    def __iter__(cls) -> Iterator[Entity]:
        return iter(cls._restricted_data())

    @classmethod
    def __len__(cls) -> int:
        return len(cls._restricted_data())

    @classmethod
    def __repr__(cls) -> str:
        return f"{cls.__name__}()"

    def __init_subclass__(cls) -> None:
        cls._data = []
        cls._restriction = {}

    @classmethod
    def _check_attr_names(cls, attr_names: Mapping[str, Any]) -> None:
        for attr_name in attr_names:
            if attr_name not in cls.attrs:
                raise ValueError(f"Table doesn't have attribute with name '{attr_name}'!")


@pytest.fixture
def fake_table() -> Type[FakeTable]:
    return cast(Type[FakeTable], type(FakeTable.__name__, (FakeTable,), {}))


class FakeAutopopulatedTable(FakeTable):
    def __init__(self) -> None:
        super().__init__()
        self.key: Optional[Entity] = None

    def make(self, key: Entity) -> None:
        self.key = key


@pytest.fixture
def fake_autopopulated_table() -> Type[FakeAutopopulatedTable]:
    return cast(Type[FakeAutopopulatedTable], type(FakeTable.__name__, (FakeAutopopulatedTable,), {}))


T = TypeVar("T", bound=Table)


class FakeSchema:
    schema_tables: Dict[str, Type[Table]] = {}

    def __init__(self, schema_name: str, connection: FakeConnection) -> None:
        self.database = schema_name
        self.connection = connection
        self.decorated_tables: Dict[str, Type[Table]] = {}
        self.context: Dict[str, Type[Table]] = {}

    def __call__(self, cls: Type[T], *, context: Optional[Mapping[str, Type[Table]]] = None) -> Type[T]:
        if context:
            self.context = dict(context)
        self.decorated_tables[cls.__name__] = cls
        cls.database = self.database
        cls.connection = self.connection
        return cls

    def spawn_missing_classes(self, context: MutableMapping[str, Type[Table]]) -> None:
        context.update(self.schema_tables)

    def __repr__(self) -> str:
        return "FakeSchema()"


@pytest.fixture
def fake_schema(fake_connection: FakeConnection, fake_table: Type[Table]) -> FakeSchema:
    FakeSchema.schema_tables[fake_table.__name__] = fake_table

    return FakeSchema("schema", fake_connection)
