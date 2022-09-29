"""Contains the DataJoint specific unit of work."""
from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from ..service.abstract import Repository, UnitOfWork
from .abstract import AbstractConnection


class DJUnitOfWork(UnitOfWork):
    """Represents a DataJoint specific unit of work."""

    def __init__(self, connection: AbstractConnection, records: Repository) -> None:
        """Initialize the unit of work."""
        self.connection = connection
        self.records = records

    def __enter__(self) -> DJUnitOfWork:
        """Enter the unit of work."""
        self.connection.open()
        self.connection.transaction.start()
        return super().__enter__()

    def commit(self) -> None:
        """Commit the unit of work."""
        self.connection.transaction.commit()

    def rollback(self) -> None:
        """Rollback the unit of work."""
        self.connection.transaction.rollback()

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        """Exit the unit of work."""
        super().__exit__(exc_type, exc, traceback)
        self.connection.close()

    def __repr__(self) -> str:
        """Return a string representation of the unit of work."""
        return f"{self.__class__.__name__}(connection={repr(self.connection)}, records={repr(self.records)})"
