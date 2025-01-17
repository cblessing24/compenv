"""This package contains adapters adapting between external systems and the domain/service layers."""
from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Any

from ..service import SERVICE_CLASSES, initialize_services
from .abstract import AbstractConnection, AbstractTable
from .controller import DJController
from .distribution import DistributionConverter
from .entity import DJComputationRecord
from .presenter import PrintingPresenter
from .repository import DJRepository
from .translator import DJTranslator, blake2b
from .unit_of_work import DJUnitOfWork


@dataclasses.dataclass(frozen=True)
class DJAdapters:
    """A set of DataJoint adapters."""

    translator: DJTranslator
    controller: DJController
    presenter: PrintingPresenter
    repo: DJRepository


def create_dj_adapters(table: AbstractTable[DJComputationRecord], connection: AbstractConnection) -> DJAdapters:
    """Create a set of DataJoint adapters using the given table and connection."""
    translator = DJTranslator(blake2b)
    presenter = PrintingPresenter(print_=print)
    repo = DJRepository(table=table, translator=translator)
    uow = DJUnitOfWork(connection=connection, records=repo)
    output_ports: dict[str, Callable[[Any], None]] = {"record": presenter.record, "diff": presenter.diff}
    dependencies = {"uow": uow, "distribution_finder": DistributionConverter()}
    services = initialize_services(
        SERVICE_CLASSES,
        output_ports=output_ports,
        dependencies=dependencies,
    )
    controller = DJController(services=services, translator=translator)
    return DJAdapters(translator=translator, presenter=presenter, repo=repo, controller=controller)
