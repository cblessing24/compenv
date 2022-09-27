"""This package contains the infrastructure layer."""
import dataclasses

from .connection import ConnectionFacade, ConnectionFactory
from .schema import SchemaFactory
from .table import TableFacade, TableFactory
from .types import Schema


@dataclasses.dataclass(frozen=True)
class DJInfrastructure:
    """A set of DataJoint infrastructure objects."""

    factory: TableFactory
    facade: TableFacade
    connection: ConnectionFacade


def create_dj_infrastructure(schema: Schema, table_name: str) -> DJInfrastructure:
    """Create a set of DataJoint infrastructure objects."""
    connection_info = schema.connection.conn_info
    connection_factory = ConnectionFactory(connection_info["host"], connection_info["user"], connection_info["passwd"])
    connection = ConnectionFacade(connection_factory)
    schema_factory = SchemaFactory(schema.database, connection=connection)
    table_factory = TableFactory(schema_factory, parent=table_name)
    table = TableFacade(factory=table_factory)
    return DJInfrastructure(factory=table_factory, facade=table, connection=connection)
