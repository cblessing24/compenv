"""Contains repository code."""
from abc import ABC, abstractmethod
from typing import Iterator

from ..model.computation import ComputationRecord


class ComputationRecordRepository(ABC):
    """Defines the interface for the repository containing computation records."""

    @abstractmethod
    def add(self, computation_record: ComputationRecord) -> None:
        """Add the given computation record to the repository if it does not already exist."""

    @abstractmethod
    def remove(self, identifier: str) -> None:
        """Remove the computation record matching the given identifier from the repository if it exists."""

    @abstractmethod
    def get(self, identifier: str) -> ComputationRecord:
        """Get the computation record matching the given identifier from the repository if it exists."""

    @abstractmethod
    def list(self) -> Iterator[ComputationRecord]:
        """Iterate over the computation records in the repository."""
