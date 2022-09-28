"""Contains the DataJoint specific unit of work."""
from __future__ import annotations

from ..service.abstract import Repository, UnitOfWork
from .abstract import AbstractConnectionFacade


class DJUnitOfWork(UnitOfWork):
    """Represents a DataJoint specific unit of work."""

    def __init__(self, connection: AbstractConnectionFacade, records: Repository) -> None:
        """Initialize the unit of work."""
        self.connection = connection
        self.records = records

    def __enter__(self) -> DJUnitOfWork:
        """Enter the unit of work."""
        if not self.connection.in_transaction:
            self.connection.start()
        return super().__enter__()

    def commit(self) -> None:
        """Commit the unit of work."""
        self.connection.commit()

    def rollback(self) -> None:
        """Rollback the unit of work."""
        self.connection.rollback()
