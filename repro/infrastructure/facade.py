"""Contains code related to facades for DataJoint tables."""
import dataclasses

from datajoint.errors import DuplicateError
from datajoint.table import Table

from ..adapters.repository import AbstractTableFacade, DJComputationRecord
from ..adapters.translator import PrimaryKey


class RecordTableFacade(AbstractTableFacade[DJComputationRecord]):
    """Facade around a DataJoint table that stores computation records."""

    def __init__(self, table: Table) -> None:
        """Initialize the record table facade."""
        self.table = table

    def insert(self, entity: DJComputationRecord) -> None:
        """Insert the record into the record table and its parts.

        Raises:
            ValueError: Record already exists.
        """
        try:
            self.table.insert1(entity.primary)
        except DuplicateError as error:
            raise ValueError(f"Computation record with primary key '{entity.primary}' already exists!") from error
        for part, (attr, _) in DJComputationRecord.parts.items():
            getattr(self.table, part)().insert([entity.primary | dataclasses.asdict(e) for e in getattr(entity, attr)])

    def delete(self, primary: PrimaryKey) -> None:
        """Delete the record matching the given primary key from the record table and its parts.

        Raises:
            KeyError: No record matching the given primary key exists.
        """
        if primary not in self.table:
            raise KeyError(f"Computation record with primary key '{primary}' does not exist!")
        for part in DJComputationRecord.parts:
            (getattr(self.table, part)() & primary).delete_quick()
        (self.table & primary).delete_quick()

    def fetch(self, primary: PrimaryKey) -> DJComputationRecord:
        """Fetch the record matching the given primary key from the record table and its parts.

        Raises:
            KeyError: No record matching the given primary key exists.
        """
        if primary not in self.table:
            raise KeyError(f"Computation record with primary key '{primary}' does not exist!")
        entities = {}
        for part, (attr, entity_cls) in DJComputationRecord.parts.items():
            part_entities = (getattr(self.table, part)() & primary).fetch(as_dict=True)
            part_entities = [dict(e.items() - primary.items()) for e in part_entities]
            part_entities = [entity_cls(**e) for e in part_entities]  # type: ignore
            entities[attr] = frozenset(part_entities)
        return DJComputationRecord(primary, **entities)

    def __repr__(self) -> str:
        """Return a string representation of the record table facade."""
        return f"{self.__class__.__name__}(table={repr(self.table)})"
