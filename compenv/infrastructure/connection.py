"""Contains code related to DataJoint's connection object."""
from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Optional, Type, TypedDict

from datajoint.connection import Connection as DJConnection

from ..adapters.abstract import AbstractConnection, AbstractTransaction
from . import types


class Connection(AbstractConnection):
    """Represents a facade around the connection specific parts of DataJoint's connection object."""

    def __init__(self, factory: types.ConnectionFactory) -> None:
        """Initialize the connection."""
        self._factory = factory
        self._dj_connection: Optional[types.Connection] = None
        self._transaction = _Transaction(self)

    @property
    def transaction(self) -> _Transaction:
        """Return the transaction."""
        return self._transaction

    @property
    def dj_connection(self) -> types.Connection:
        """Return the DataJoint connection if it exists."""
        if not self._dj_connection:
            raise RuntimeError("Not connected")
        return self._dj_connection

    def open(self) -> None:
        """Open a new connection."""
        self._dj_connection = self._factory()

    def close(self) -> None:
        """Close the connection."""
        self.dj_connection.close()
        self._dj_connection = None

    def __enter__(self) -> None:
        """Open a new connection on entering the context."""
        self.open()

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        """Close the connection on exiting the context."""
        self.close()

    def __repr__(self) -> str:
        """Return a string representation of the connection facade."""
        return f"{self.__class__.__name__}(factory={repr(self._factory)})"


class _Transaction(AbstractTransaction):
    """Represents a facade around the transaction specific parts of DataJoint's connection object."""

    def __init__(self, connection: Connection) -> None:
        """Initialize the transaction."""
        self._connection = connection

    def start(self) -> None:
        """Start a transaction."""
        self._connection.dj_connection.start_transaction()

    def commit(self) -> None:
        """Commit the transaction."""
        self._connection.dj_connection.commit_transaction()

    def rollback(self) -> None:
        """Rollback the transaction."""
        self._connection.dj_connection.cancel_transaction()


class ConnectionOptionsDict(TypedDict):
    """A dictionary containing optional arguments for DataJoint's connection object."""

    port: Optional[int]
    init_fun: Optional[Callable[[], str]]
    use_tls: Optional[bool]


DEFAULT_OPTIONS = {"port": None, "init_fun": None, "use_tls": None}


class DJConnectionFactory:
    """A factory producing DataJoint connections."""

    def __init__(self, host: str, user: str, password: str, options: Optional[ConnectionOptionsDict] = None) -> None:
        """Initialize the factory."""
        self.host = host
        self.user = user
        self.password = password
        self.options = options if options else DEFAULT_OPTIONS

    def __call__(self) -> DJConnection:
        """Create a new DataJoint connection."""
        return DJConnection(host=self.host, user=self.user, password=self.password, **self.options)

    def __repr__(self) -> str:
        """Return a string representation of the factory."""
        args_string = ", ".join(f"{a}={repr(v)}" for a, v in self.__dict__.items() if not a.startswith("_"))
        return f"{self.__class__.__name__}({args_string})"
