"""Contains interface definitions expected by the service layer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterator, MutableMapping, Type, TypeVar

from ..model.computation import ComputationRecord, Identifier


class Request(ABC):  # pylint: disable=too-few-public-methods
    """Defines the interface for all requests."""


class Response(ABC):  # pylint: disable=too-few-public-methods
    """Defines the interface for all responses."""


_T = TypeVar("_T", bound=Request)
_V = TypeVar("_V", bound=Response)


class Service(ABC, Generic[_T, _V]):
    """Defines the interface for all services."""

    _request_cls: Type[_T]
    _response_cls: Type[_V]

    def __init__(self, repo: Repository, output_port: Callable[[_V], None]) -> None:
        """Initialize the service."""
        self.repo = repo
        self.output_port = output_port

    def __call__(self, request: _T) -> None:
        """Pass the response of the executed service to the output port."""
        response = self._execute(request)
        self.output_port(response)

    @abstractmethod
    def _execute(self, request: _T) -> _V:
        """Execute the service with the given request."""

    @property
    def create_request(self) -> Type[_T]:
        """Create a new request from the given arguments."""
        return self._request_cls


class Repository(ABC, MutableMapping[Identifier, ComputationRecord]):
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
