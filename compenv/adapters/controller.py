"""Contains the controller."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Callable, Protocol, Type, TypeVar

from ..service.abstract import Request
from ..service.record import RecordRequest
from .translator import Translator

if TYPE_CHECKING:
    from datajoint.table import Entity

    from ..types import PrimaryKey


_T = TypeVar("_T", bound=Request)


class Service(Protocol[_T]):
    """Define the service interface as expected by the controller."""

    @property
    def create_request(self) -> Type[_T]:
        """Return the request class."""

    def __call__(self, request: _T) -> None:
        """Execute the service."""


class DJController:
    """Controls the execution of services."""

    def __init__(self, record_service: Service[RecordRequest], translator: Translator[PrimaryKey]) -> None:
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
