"""Contains abstract base classes defining interfaces used by code in the adapter layer."""
from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Iterator, Mapping, MutableMapping, Type, TypeVar

if TYPE_CHECKING:
    from datajoint.table import PrimaryKey


@dataclasses.dataclass(frozen=True)
class MasterEntity:
    """Base class for all classes representing DataJoint entities in master tables."""

    parts: ClassVar[list[Type[PartEntity]]] = []


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


class AbstractTableFacade(ABC, MutableMapping["PrimaryKey", _T], Generic[_T]):
    """Defines the interface for all table facades."""

    @abstractmethod
    def __setitem__(self, primary: PrimaryKey, master_entity: _T) -> None:
        """Insert the given entity into the table under the given primary key if it does not already exist.

        Raises:
            ValueError: The primary key already exists.
        """

    @abstractmethod
    def __delitem__(self, primary: PrimaryKey) -> None:
        """Delete the entity matching the given primary key from the table if it exists.

        Raises:
            KeyError: No entity matching the given key exists.
        """

    @abstractmethod
    def __getitem__(self, primary: PrimaryKey) -> _T:
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
