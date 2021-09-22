"""Contains interface definitions expected by the service layer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from typing import Generic, Iterator, Type, TypeVar

from ..model.computation import ComputationRecord, Identifier


class Request(ABC):  # pylint: disable=too-few-public-methods
    """Defines the interface for all requests."""


_T = TypeVar("_T", bound=Request)


class Service(ABC, Generic[_T]):
    """Defines the interface for all services."""

    _request_cls: Type[_T]

    def __init__(self, repo: ComputationRecordRepository) -> None:
        """Initialize the service."""
        self.repo = repo

    @abstractmethod
    def __call__(self, request: _T) -> None:
        """Execute the service with the given request."""

    def create_request(self, *args, **kwargs) -> _T:
        """Create a new request from the given arguments."""
        return self._request_cls(*args, **kwargs)


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
