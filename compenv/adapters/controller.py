"""Contains the controller."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Callable

from compenv.service.abstract import Repository

from ..service.record import RecordService
from .presenter import Presenter
from .translator import Translator

if TYPE_CHECKING:
    from datajoint.table import Entity

    from ..types import PrimaryKey


class DJController:
    """Controls the execution of services."""

    def __init__(self, repo: Repository, translator: Translator[PrimaryKey], presenter: Presenter) -> None:
        """Initialize the controller."""
        self.repo = repo
        self.translator = translator
        self.presenter = presenter

    def record(self, key: PrimaryKey, make: Callable[[Entity], None]) -> None:
        """Execute the record service."""
        ident = self.translator.to_internal(key)
        service = RecordService(self.repo, output_port=self.presenter.record)
        trigger = functools.partial(make, key)
        request = service.create_request(ident, trigger=trigger)
        service(request)

    def __repr__(self) -> str:
        """Return a string representation of the controller."""
        return (
            f"{self.__class__.__name__}(repo={repr(self.repo)},"
            f" translator={repr(self.translator)}, presenter={repr(self.presenter)})"
        )
