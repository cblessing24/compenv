"""Contains code related to facades for DataJoint tables."""
from __future__ import annotations

import dataclasses
import functools
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, TypeVar

from datajoint.errors import DuplicateError

from ..adapters.abstract import AbstractTableFacade
from ..adapters.entity import DJComputationRecord
from .factory import DJTableFactory

if TYPE_CHECKING:
    from datajoint.table import PrimaryKey

    _T = TypeVar("_T")


def _check_primary(func: Callable[[DJTableFacade, PrimaryKey], _T]) -> Callable[[DJTableFacade, PrimaryKey], _T]:
    @functools.wraps(func)
    def wrapper(self: DJTableFacade, primary: PrimaryKey) -> _T:
        if primary not in self.factory():
            raise KeyError(f"Computation record with primary key '{primary}' does not exist!")
        return func(self, primary)

    return wrapper


class DJTableFacade(AbstractTableFacade[DJComputationRecord]):
    """Facade around a DataJoint table that stores computation records."""

    def __init__(self, factory: DJTableFactory) -> None:
        """Initialize the record table facade."""
        self.factory = factory

    def __setitem__(self, primary: PrimaryKey, master_entity: DJComputationRecord) -> None:
        """Insert the record into the record table and its parts.

        Raises:
            ValueError: Record already exists.
        """
        try:
            self.factory().insert1(primary)
        except DuplicateError as error:
            raise ValueError(f"Computation record with primary key '{primary}' already exists!") from error
        for part in DJComputationRecord.parts:
            getattr(self.factory(), part.__name__)().insert(
                [{**primary, **dataclasses.asdict(e)} for e in getattr(master_entity, part.master_attr)]
            )

    @_check_primary
    def __delitem__(self, primary: PrimaryKey) -> None:
        """Delete the record matching the given primary key from the record table and its parts.

        Raises:
            KeyError: No record matching the given primary key exists.
        """
        for part in DJComputationRecord.parts:
            (getattr(self.factory(), part.__name__)() & primary).delete_quick()
        (self.factory() & primary).delete_quick()

    @_check_primary
    def __getitem__(self, primary: PrimaryKey) -> DJComputationRecord:
        """Fetch the record matching the given primary key from the record table and its parts.

        Raises:
            KeyError: No record matching the given primary key exists.
        """
        entities = {}
        for part in DJComputationRecord.parts:
            part_entities = (getattr(self.factory(), part.__name__)() & primary).fetch(as_dict=True)
            part_entities = [dict(e.items() - primary.items()) for e in part_entities]
            part_entities = [part.from_mapping(e) for e in part_entities]
            entities[part.master_attr] = frozenset(part_entities)
        return DJComputationRecord(**entities)

    def __iter__(self) -> Iterator[PrimaryKey]:
        """Iterate over the primary keys of all the records in the table."""
        return iter(self.factory())

    def __len__(self) -> int:
        """Return the number of records in the table."""
        return len(self.factory())

    def __repr__(self) -> str:
        """Return a string representation of the record table facade."""
        return f"{self.__class__.__name__}(factory={repr(self.factory)})"
