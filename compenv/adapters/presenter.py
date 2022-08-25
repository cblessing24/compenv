"""Contains the presenter."""
from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from compenv.service.diff import DiffResponse

from ..service.record import RecordResponse


class Presenter(Protocol):  # pylint: disable=too-few-public-methods
    """Presents information contained within service responses."""

    def record(self, response: RecordResponse) -> None:
        """Present information contained within the record service's response."""


class PrintingPresenter:
    """Prints information contained within service responses."""

    def __init__(self, print_: Callable[[str], None]):
        """Initialize the presenter."""
        self.print = print_

    def record(self, response: RecordResponse) -> None:
        """Print information contained within the record service's response."""

    def diff(self, response: DiffResponse) -> None:
        """Print information contained withing the diff service's response."""
        if response.differ:
            self.print("The computation records differ")
        else:
            self.print("The computation records do not differ")

    def __repr__(self) -> str:
        """Return a string representation of the presenter."""
        return f"{self.__class__.__name__}(print={repr(self.print)})"
