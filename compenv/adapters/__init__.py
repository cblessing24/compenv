"""This package contains adapters adapting between external systems and the domain/service layers."""
import dataclasses

from ..service import SERVICE_CLASSES, initialize_services
from .abstract import AbstractTableFacade
from .controller import DJController
from .distribution import DistributionConverter
from .entity import DJComputationRecord
from .presenter import PrintingPresenter
from .repository import DJRepository
from .translator import DJTranslator, blake2b


@dataclasses.dataclass(frozen=True)
class DJAdapters:
    """A set of DataJoint adapters."""

    translator: DJTranslator
    controller: DJController
    presenter: PrintingPresenter
    repo: DJRepository


def create_dj_adapters(facade: AbstractTableFacade[DJComputationRecord]) -> DJAdapters:
    """Create a set of DataJoint adapters using the given facade."""
    translator = DJTranslator(blake2b)
    presenter = PrintingPresenter(print_=print)
    repo = DJRepository(facade=facade, translator=translator)
    output_ports = {"record": presenter.record}
    dependencies = {"repo": repo, "distribution_finder": DistributionConverter()}
    services = initialize_services(
        SERVICE_CLASSES,
        output_ports=output_ports,
        dependencies=dependencies,
    )
    controller = DJController(services=services, translator=translator)
    return DJAdapters(translator=translator, presenter=presenter, repo=repo, controller=controller)
