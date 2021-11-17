"""This package contains the infrastructure layer."""
import dataclasses

from datajoint import Schema

from .facade import DJTableFacade
from .factory import DJTableFactory


@dataclasses.dataclass(frozen=True)
class DJInfrastructure:
    """A set of DataJoint infrastructure objects."""

    factory: DJTableFactory
    facade: DJTableFacade


def create_dj_infrastructure(schema: Schema, table_name: str) -> DJInfrastructure:
    """Create a set of DataJoint infrastructure objects."""
    factory = DJTableFactory(schema, parent=table_name)
    facade = DJTableFacade(factory=factory)
    return DJInfrastructure(factory=factory, facade=facade)
