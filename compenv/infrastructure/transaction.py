"""Contains transaction related code."""
from datajoint.connection import Connection

from ..adapters.abstract import AbstractTransactionFacade


class TransactionFacade(AbstractTransactionFacade):
    """Represents a facade around DataJoint's transaction interface."""

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
