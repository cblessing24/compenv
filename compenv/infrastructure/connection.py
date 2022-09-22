"""Contains code related to DataJoint's connection object."""
from ..adapters.abstract import AbstractConnectionFacade
from .types import Connection


class ConnectionFacade(AbstractConnectionFacade):
    """Represents a facade around DataJoint's connection object."""

    def __init__(self, connection: Connection) -> None:
        """Initialize the transaction."""
        self._connection = connection

    def start(self) -> None:
        """Start a transaction."""
        self._connection.start_transaction()

    def commit(self) -> None:
        """Commit the transaction."""
        self._connection.commit_transaction()

    def rollback(self) -> None:
        """Rollback the transaction."""
        self._connection.cancel_transaction()

    @property
    def in_transaction(self) -> bool:
        """Return True if we are in a transaction, False otherwise."""
        return self._connection.in_transaction

    def close(self) -> None:
        """Close the connection."""
        self._connection.close()