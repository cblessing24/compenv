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
    """A factory producing DataJoint connections."""

    def __init__(self, host: str, user: str, password: str, options: Optional[ConnectionOptionsDict] = None) -> None:
        """Initialize the factory."""
        self.host = host
        self.user = user
        self.password = password
        self.options = options if options else DEFAULT_OPTIONS
        self._dj_connection: Optional[DJConnection] = None

    @property
    def dj_connection(self) -> DJConnection:
        """Return the last created DataJoint connection if it exists."""
        if self._dj_connection is None:
            raise RuntimeError("Connection is missing")
        return self._dj_connection

    def __call__(self) -> DJConnection:
        """Create a new DataJoint connection."""
        self._dj_connection = DJConnection(host=self.host, user=self.user, password=self.password, **self.options)
        return self.dj_connection

    def __repr__(self) -> str:
        """Return a string representation of the factory."""
        args_string = ", ".join(f"{a}={repr(v)}" for a, v in self.__dict__.items() if not a.startswith("_"))
        return f"{self.__class__.__name__}({args_string})"
