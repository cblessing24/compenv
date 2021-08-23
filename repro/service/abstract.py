"""Contains interface definitions expected by the service layer."""
from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from typing import Iterator

from ..model.computation import ComputationRecord, Identifier


class ComputationRecordRepository(ABC, MutableMapping):
    """Defines the interface for the repository containing computation records."""

    @abstractmethod
    def __setitem__(self, identifier: Identifier, comp_rec: ComputationRecord) -> None:
        """Add the given computation record to the repository if it does not already exist."""

    @abstractmethod
    def __delitem__(self, identifier: Identifier) -> None:
        """Remove the computation record matching the given identifier from the repository if it exists."""

    @abstractmethod
    def __getitem__(self, identifier: Identifier) -> ComputationRecord:
        """Get the computation record matching the given identifier from the repository if it exists."""

    @abstractmethod
    def __iter__(self) -> Iterator[Identifier]:
        """Iterate over the identifiers of all computation records."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of computation records in the repository."""
