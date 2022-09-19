"""Contains the DataJoint specific unit of work."""
from __future__ import annotations

from typing import Protocol

from ..service.abstract import Repository, UnitOfWork


class Connection(Protocol):
    """DataJoint connection protocol."""

    def start_transaction(self) -> None:
        """Start a transaction."""

    def commit_transaction(self) -> None:
        """Commit the transaction."""

    def cancel_transaction(self) -> None:
        """Cancel the transaction."""

    @property
    def in_transaction(self) -> bool:
        """Return True if we are currently in a transaction, False otherwise."""


class DJUnitOfWork(UnitOfWork):
    """Represents a DataJoint specific unit of work."""

    def __init__(self, connection: Connection, records: Repository) -> None:
        """Initialize the unit of work."""
        self.connection = connection
        self.records = records

    def __enter__(self) -> DJUnitOfWork:
        """Enter the unit of work."""
        if not self.connection.in_transaction:
            self.connection.start_transaction()
        return super().__enter__()

    def commit(self) -> None:
        """Commit the unit of work."""
        self.connection.commit_transaction()

    def rollback(self) -> None:
        """Rollback the unit of work."""
        self.connection.cancel_transaction()
