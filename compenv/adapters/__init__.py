"""This package contains adapters adapting between external systems and the domain/service layers."""
import dataclasses

from compenv.adapters.distribution import DistributionConverter
from compenv.service.record import RecordService

from .abstract import AbstractTableFacade
from .controller import DJController
from .entity import DJComputationRecord
from .presenter import DJPresenter
from .repository import DJRepository
from .translator import DJTranslator, blake2b


@dataclasses.dataclass(frozen=True)
class DJAdapters:
    """A set of DataJoint adapters."""

    translator: DJTranslator
    controller: DJController
    presenter: DJPresenter
    repo: DJRepository


def create_dj_adapters(facade: AbstractTableFacade[DJComputationRecord]) -> DJAdapters:
    """Create a set of DataJoint adapters using the given facade."""
    translator = DJTranslator(blake2b)
    presenter = DJPresenter()
    repo = DJRepository(facade=facade, translator=translator)
    record_service = RecordService(output_port=presenter.record, repo=repo, distribution_finder=DistributionConverter())
    controller = DJController(record_service=record_service, translator=translator)
    return DJAdapters(translator=translator, presenter=presenter, repo=repo, controller=controller)
