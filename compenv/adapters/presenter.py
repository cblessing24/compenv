"""Contains the presenter."""
from ..service.record import RecordResponse


class DJPresenter:
    """Presents information contained within service responses."""

    def record(self, response: RecordResponse) -> None:
        """Present information contained within the record service's response."""

    def __repr__(self) -> str:
        """Return a string representation of the presenter."""
        return self.__class__.__name__ + "()"
