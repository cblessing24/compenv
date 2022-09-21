"""This package contains the infrastructure layer."""
import dataclasses

from .connection import ConnectionFacade
from .table import DJTableFacade, DJTableFactory
from .types import Schema


@dataclasses.dataclass(frozen=True)
class DJInfrastructure:
    """A set of DataJoint infrastructure objects."""

    factory: DJTableFactory
    facade: DJTableFacade
    connection: ConnectionFacade


def create_dj_infrastructure(schema: Schema, table_name: str) -> DJInfrastructure:
    """Create a set of DataJoint infrastructure objects."""
    factory = DJTableFactory(schema, parent=table_name)
    facade = DJTableFacade(factory=factory)
    connection = ConnectionFacade(schema.connection)
    return DJInfrastructure(factory=factory, facade=facade, connection=connection)
