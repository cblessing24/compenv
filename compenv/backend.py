"""Contains setup code for the backend."""
import dataclasses

from datajoint import Schema

from .adapters import DJAdapters, create_dj_adapters
from .infrastructure import DJInfrastructure, create_dj_infrastructure


@dataclasses.dataclass(frozen=True)
class DJBackend:
    """DataJoint-specific backend."""

    infra: DJInfrastructure
    adapters: DJAdapters


def create_dj_backend(schema: Schema, table_name: str) -> DJBackend:
    """Create backend made up of all the DataJoint specific parts."""
    infra = create_dj_infrastructure(schema, table_name)
    adapters = create_dj_adapters(infra.facade)
    return DJBackend(infra=infra, adapters=adapters)
