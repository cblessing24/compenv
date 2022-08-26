"""Contains custom types used in the infrastructure layer."""
from __future__ import annotations

from typing import Container, Dict, Iterable, Mapping, MutableMapping, Optional, Protocol, Sized, Type, TypeVar, Union

from ..types import PrimaryKey

Entity = Mapping[str, Union[str, float, int]]


class Table(
    Sized, Iterable[Entity], Container[object], Protocol
):  # pylint: disable=abstract-method,too-few-public-methods
    """Datajoint table protocol."""

    definition: str
    database: str
    connection: Connection

    def insert1(self, row: Entity) -> None:
        """Insert a row into the table."""


class Connection(Protocol):  # pylint: disable=too-few-public-methods
    """Datajoint connection protocol."""


class AutopopulatedTable(Table, Protocol):  # pylint: disable=abstract-method
    """Datajoint auto-populated table protocol."""

    def make(self, key: PrimaryKey) -> None:
        """Make the entity corresponding to the given primary key."""


class Factory(Protocol):  # pylint: disable=too-few-public-methods
    """Datajoint table factory protocol."""

    def __call__(self) -> Table:
        """Return a object that supports the table protocol."""


Context = MutableMapping[str, object]
_T = TypeVar("_T", bound=Table)


class Schema(Protocol):
    """Datajoint schema protocol."""

    context: Dict[str, object]

    def spawn_missing_classes(self, context: Context) -> None:
        """Place missing tables in the context."""

    def __call__(self, cls: Type[_T], *, context: Optional[Mapping[str, object]] = None) -> Type[_T]:
        """Bind the supplied class to the schema."""
