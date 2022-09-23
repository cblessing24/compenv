"""Contains code related to DataJoint's schema object."""
from datajoint.schemas import Schema

from .connection import ConnectionFactory


class SchemaFactory:
    """A factory producing schemas."""

    def __init__(self, name: str, connection_factory: ConnectionFactory) -> None:
        """Initialize the schema factory."""
        self._name = name
        self._connection_factory = connection_factory

    def __call__(self) -> Schema:
        """Produce a new schema."""
        return Schema(self._name, connection=self._connection_factory.dj_connection)

    def __repr__(self) -> str:
        """Return a string representation of the factory."""
        return f"{self.__class__.__name__}(name={self._name}, connection_factory={self._connection_factory})"
