"""Contains the controller."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Callable

from ..service.record import RecordService
from .translator import Translator

if TYPE_CHECKING:
    from datajoint.table import Entity

    from ..types import PrimaryKey


class DJController:
    """Controls the execution of services."""

    def __init__(self, record_service: RecordService, translator: Translator[PrimaryKey]) -> None:
        """Initialize the controller."""
        self.record_service = record_service
        self.translator = translator

    def record(self, key: PrimaryKey, make: Callable[[Entity], None]) -> None:
        """Execute the record service."""
        ident = self.translator.to_internal(key)
        trigger = functools.partial(make, key)
        request = self.record_service.create_request(ident, trigger=trigger)
        self.record_service(request)

    def __repr__(self) -> str:
        """Return a string representation of the controller."""
        return (
            f"{self.__class__.__name__}(record_service={repr(self.record_service)},"
            f" translator={repr(self.translator)})"
        )
