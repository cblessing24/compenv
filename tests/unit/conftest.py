from __future__ import annotations

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
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
)

import pytest
from datajoint.errors import DuplicateError

from compenv.adapters.entity import DJComputationRecord, DJDistribution
from compenv.infrastructure.types import Connection, Table
from compenv.model.record import ComputationRecord, Distribution, Identifier
from compenv.service.abstract import DistributionFinder, Repository, Response
from compenv.types import PrimaryKey

if TYPE_CHECKING:
    from datajoint.table import Entity


@pytest.fixture
def distributions() -> frozenset[Distribution]:
    return frozenset({Distribution("dist1", "0.1.0"), Distribution("dist2", "0.1.1")})


@pytest.fixture
def computation_record(identifier: Identifier, distributions: frozenset[Distribution]) -> ComputationRecord:
    return ComputationRecord(identifier=identifier, distributions=distributions)


@pytest.fixture
def primary() -> Dict[str, int]:
    return {"a": 0, "b": 1}


@pytest.fixture
def dj_dists() -> FrozenSet[DJDistribution]:
    return frozenset(
        [
            DJDistribution(distribution_name="dist1", distribution_version="0.1.0"),
            DJDistribution(distribution_name="dist2", distribution_version="0.1.1"),
        ]
    )


@pytest.fixture
def dj_comp_rec(
    primary: PrimaryKey,
    dj_dists: FrozenSet[DJDistribution],
) -> DJComputationRecord:
    return DJComputationRecord(primary=primary, distributions=dj_dists)


class FakeTrigger:
    triggered = False

    def __call__(self) -> None:
        self.triggered = True

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
    def __init__(self, internal_to_external: Mapping[Identifier, PrimaryKey]) -> None:
        self._internal_to_external = internal_to_external

    def to_internal(self, primary: PrimaryKey) -> Identifier:
        return next(internal for internal, external in self._internal_to_external.items() if external == primary)

    def to_external(self, identifier: Identifier) -> PrimaryKey:
        return self._internal_to_external[identifier]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class FakeTranslatorFactory(Protocol):
    def __call__(self, internal_to_external: Optional[Mapping[Identifier, PrimaryKey]] = None) -> FakeTranslator:
        ...


@pytest.fixture
def fake_translator_factory(identifier: Identifier, primary: PrimaryKey) -> FakeTranslatorFactory:
    def factory(internal_to_external: Optional[Mapping[Identifier, PrimaryKey]] = None) -> FakeTranslator:
        if internal_to_external is None:
            internal_to_external = {identifier: primary}
        return FakeTranslator(internal_to_external)

    return factory


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
        self.context: Dict[str, object] = {}

    def __call__(self, cls: Type[T], *, context: Optional[Mapping[str, object]] = None) -> Type[T]:
        if context:
            self.context = dict(context)
        self.decorated_tables[cls.__name__] = cls
        cls.database = self.database
        cls.connection = self.connection
        return cls

    def spawn_missing_classes(self, context: MutableMapping[str, object]) -> None:
        context.update(self.schema_tables)

    def __repr__(self) -> str:
        return "FakeSchema()"


@pytest.fixture
def fake_schema(fake_connection: FakeConnection, fake_table: Type[Table]) -> FakeSchema:
    FakeSchema.schema_tables[fake_table.__name__] = fake_table

    return FakeSchema("schema", fake_connection)


class FakeOutputPort:
    def __init__(self) -> None:
        self.responses: list[Response] = []

    def __call__(self, response: Response) -> None:
        self.responses.append(response)


@pytest.fixture
def fake_output_port() -> FakeOutputPort:
    return FakeOutputPort()


class FakeDistributionFinder(DistributionFinder):
    def __init__(self, distributions: frozenset[Distribution]) -> None:
        self.distributions = distributions

    def __call__(self) -> frozenset[Distribution]:
        return self.distributions


@pytest.fixture
def fake_distribution_finder(distributions: frozenset[Distribution]) -> FakeDistributionFinder:
    return FakeDistributionFinder(distributions)
