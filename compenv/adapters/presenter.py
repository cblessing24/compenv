"""Contains the presenter."""
from typing import Protocol

from compenv.service.diff import DiffResponse

from ..service.record import RecordResponse


class Presenter(Protocol):  # pylint: disable=too-few-public-methods
    """Presents information contained within service responses."""

    def record(self, response: RecordResponse) -> None:
        """Present information contained within the record service's response."""


class DJPresenter:
    """Presents information contained within service responses."""

    def record(self, response: RecordResponse) -> None:
        """Present information contained within the record service's response."""

    def diff(self, response: DiffResponse) -> None:
        """Present information contained withing the diff service's response."""
        if response.differ:
            print("The computation records differ")
        else:
            print("The computation records do not differ")

    def __repr__(self) -> str:
        """Return a string representation of the presenter."""
        return self.__class__.__name__ + "()"
