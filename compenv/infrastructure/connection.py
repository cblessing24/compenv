"""Contains code related to DataJoint's connection object."""
from __future__ import annotations

from collections.abc import Callable
from typing import Optional, TypedDict

from datajoint.connection import Connection as DJConnection

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

    def __repr__(self) -> str:
        """Return a string representation of the connection facade."""
        return f"{self.__class__.__name__}(connection={repr(self._connection)})"


class ConnectionOptionsDict(TypedDict):
    """A dictionary containing optional arguments for DataJoint's connection object."""

    port: Optional[int]
    init_fun: Optional[Callable[[], str]]
    use_tls: Optional[bool]


DEFAULT_OPTIONS = {"port": None, "init_fun": None, "use_tls": None}


class ConnectionFactory:
    """A factory producing connections."""

    def __init__(self, host: str, user: str, password: str, options: Optional[ConnectionOptionsDict] = None) -> None:
        """Initialize the connection factory."""
        self.host = host
        self.user = user
        self.password = password
        self.options = options if options else DEFAULT_OPTIONS

    def __call__(self) -> ConnectionFacade:
        """Create a new connection."""
        return ConnectionFacade(DJConnection(host=self.host, user=self.user, password=self.password, **self.options))

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        args_string = ", ".join(f"{a}={repr(v)}" for a, v in self.__dict__.items())
        return f"{self.__class__.__name__}({args_string})"
