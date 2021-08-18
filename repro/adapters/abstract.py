"""Contains abstract base classes defining interfaces used by code in the adapter layer."""
import dataclasses
from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Type, TypeVar

from .translator import PrimaryKey


@dataclasses.dataclass(frozen=True)
class DJEntity(ABC):
    """Base class for all classes representing DataJoint entities."""

    parts: ClassVar[dict[str, tuple[str, Type["DJEntity"]]]] = {}


_T = TypeVar("_T", bound=DJEntity)


class AbstractTableFacade(ABC, Generic[_T]):
    """Defines the interface for all table facades."""

    @abstractmethod
    def insert(self, entity: _T) -> None:
        """Insert the entity into the table if it does not already exist.

        Raises:
            ValueError: The entity already exists.
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
