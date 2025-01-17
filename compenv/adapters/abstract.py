"""Contains abstract base classes defining interfaces used by code in the adapter layer."""
from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Iterator, Mapping, Type, TypeVar

if TYPE_CHECKING:
    from ..types import PrimaryKey


@dataclasses.dataclass(frozen=True)
class MasterEntity:
    """Base class for all classes representing DataJoint entities in master tables."""

    parts: ClassVar[list[Type[PartEntity]]] = []

    primary: PrimaryKey


class PartEntity:  # pylint: disable=too-few-public-methods
    """Base class for all classes representing DataJoint entities in part tables."""

    part_table: ClassVar[str]
    master_attr: ClassVar[str]

    definition: ClassVar[str]

    @classmethod
    @abstractmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> PartEntity:
        """Create an instance of the part entity from the given mapping."""


_T = TypeVar("_T", bound=MasterEntity)


class AbstractTable(ABC, Generic[_T]):
    """Defines the interface for all tables."""

    @abstractmethod
    def add(self, master_entity: _T) -> None:
        """Insert the given entity into the table if it does not already exist.

        Raises:
            ValueError: The primary key already exists.
        """

    @abstractmethod
    def get(self, primary: PrimaryKey) -> _T:
        """Fetch the entity matching the given primary key from the table if it exists.

        Raises:
            KeyError: No entity matching the given key exists.
        """

    @abstractmethod
    def __iter__(self) -> Iterator[PrimaryKey]:
        """Iterate over the primary keys of all entities in the table."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of entities in the table."""


class AbstractConnection(ABC):
    """Defines the interface for all connections."""

    @property
    def transaction(self) -> AbstractTransaction:
        """Return the transaction."""

    @abstractmethod
    def open(self) -> None:
        """Open a new connection."""

    @abstractmethod
    def close(self) -> None:
        """Close the connection."""


class AbstractTransaction(ABC):
    """Defines the interface for all transactions."""

    @abstractmethod
    def start(self) -> None:
        """Start a transaction."""

    @abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction."""
