"""This package contains the infrastructure layer."""
import dataclasses

from .facade import DJTableFacade
from .factory import DJTableFactory
from .transaction import TransactionFacade
from .types import Schema


@dataclasses.dataclass(frozen=True)
class DJInfrastructure:
    """A set of DataJoint infrastructure objects."""

    factory: DJTableFactory
    facade: DJTableFacade
    transaction: TransactionFacade


def create_dj_infrastructure(schema: Schema, table_name: str) -> DJInfrastructure:
    """Create a set of DataJoint infrastructure objects."""
    factory = DJTableFactory(schema, parent=table_name)
    facade = DJTableFacade(factory=factory)
    transaction = TransactionFacade(schema.connection)
    return DJInfrastructure(factory=factory, facade=facade, transaction=transaction)
