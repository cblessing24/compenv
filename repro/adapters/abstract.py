"""Contains abstract base classes defining interfaces used by code in the adapter layer."""
from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Type, TypeVar

from .translator import PrimaryKey


@dataclasses.dataclass(frozen=True)
class DJMasterEntity:
    """Base class for all classes representing DataJoint entities in master tables."""

    parts: ClassVar[list[Type[DJPartEntity]]] = []


@dataclasses.dataclass(frozen=True)
class DJPartEntity:
    """Base class for all classes representing DataJoint entities in part tables."""

    part_table: ClassVar[str]
    master_attr: ClassVar[str]


_T = TypeVar("_T", bound=DJMasterEntity)


class AbstractTableFacade(ABC, Generic[_T]):
    """Defines the interface for all table facades."""

    @abstractmethod
    def insert(self, primary: PrimaryKey, master_entity: _T) -> None:
        """Insert the given entity into the table under the given primary key if it does not already exist.

        Raises:
            ValueError: The primary key already exists.
        """

    @abstractmethod
    def delete(self, primary: PrimaryKey) -> None:
        """Delete the entity matching the given primary key from the table if it exists.

        Raises:
            KeyError: No entity matching the given key exists.
        """

    @abstractmethod
    def fetch(self, primary: PrimaryKey) -> _T:
        """Fetch the entity matching the given primary key from the table if it exists.

        Raises:
            KeyError: No entity matching the given key exists.
        """
