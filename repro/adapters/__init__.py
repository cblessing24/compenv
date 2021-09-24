"""This package contains adapters adapting between external systems and the domain/service layers."""
import dataclasses

from repro.adapters.controller import DJController
from repro.adapters.entity import DJComputationRecord
from repro.adapters.presenter import DJPresenter
from repro.adapters.repository import DJCompRecRepo
from repro.adapters.translator import DJTranslator, blake2b

from .abstract import AbstractTableFacade


@dataclasses.dataclass(frozen=True)
class DJAdapters:
    """A set of DataJoint adapters."""

    translator: DJTranslator
    controller: DJController
    presenter: DJPresenter
    repo: DJCompRecRepo


def create_dj_adapters(facade: AbstractTableFacade[DJComputationRecord]) -> DJAdapters:
    """Create a set of DataJoint adapters using the given facade."""
    translator = DJTranslator(blake2b)
    presenter = DJPresenter()
    repo = DJCompRecRepo(facade=facade, translator=translator)
    controller = DJController(repo=repo, translator=translator, presenter=presenter)
    return DJAdapters(translator=translator, presenter=presenter, repo=repo, controller=controller)
