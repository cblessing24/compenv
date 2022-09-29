"""This package contains the infrastructure layer."""
import dataclasses

from .connection import Connection, DJConnectionFactory
from .schema import SchemaFactory
from .table import Table, TableFactory
from .types import Schema


@dataclasses.dataclass(frozen=True)
class DJInfrastructure:
    """A set of DataJoint infrastructure objects."""

    factory: TableFactory
    table: Table
    connection: Connection


def create_dj_infrastructure(schema: Schema, table_name: str) -> DJInfrastructure:
    """Create a set of DataJoint infrastructure objects."""
    connection_info = schema.connection.conn_info
    connection_factory = DJConnectionFactory(
        connection_info["host"], connection_info["user"], connection_info["passwd"]
    )
    connection = Connection(connection_factory)
    schema_factory = SchemaFactory(schema.database, connection=connection)
    table_factory = TableFactory(schema_factory, parent=table_name)
    table = Table(factory=table_factory)
    return DJInfrastructure(factory=table_factory, table=table, connection=connection)
