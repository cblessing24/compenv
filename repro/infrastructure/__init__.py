"""This package contains the infrastructure layer."""
import dataclasses

from datajoint import Schema

from .facade import RecordTableFacade
from .factory import RecordTableFactory


@dataclasses.dataclass(frozen=True)
class DJInfrastructure:
    """A set of DataJoint infrastructure objects."""

    factory: RecordTableFactory
    facade: RecordTableFacade


def create_dj_infrastructure(schema: Schema, table_name: str) -> DJInfrastructure:
    """Create a set of DataJoint infrastructure objects."""
    factory = RecordTableFactory(schema, parent=table_name)
    facade = RecordTableFacade(factory=factory)
    return DJInfrastructure(factory=factory, facade=facade)
