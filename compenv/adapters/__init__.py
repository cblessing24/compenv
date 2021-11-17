"""This package contains adapters adapting between external systems and the domain/service layers."""
import dataclasses

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
    controller = DJController(repo=repo, translator=translator, presenter=presenter)
    return DJAdapters(translator=translator, presenter=presenter, repo=repo, controller=controller)
