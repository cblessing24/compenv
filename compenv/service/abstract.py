"""Contains interface definitions expected by the service layer."""
from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Callable, ClassVar, Generic, Iterator, Optional, Type, TypeVar

from ..model.record import ComputationRecord, Distribution, Identifier


class Request(ABC):  # pylint: disable=too-few-public-methods
    """Defines the interface for all requests."""


class Response(ABC):  # pylint: disable=too-few-public-methods
    """Defines the interface for all responses."""


_T = TypeVar("_T", bound=Request)
_V = TypeVar("_V", bound=Response)


class Service(ABC, Generic[_T, _V]):
    """Defines the interface for all services."""

    name: ClassVar[str]

    _request_cls: Type[_T]
    _response_cls: Type[_V]

    def __init__(self, *, output_port: Callable[[_V], None]) -> None:
        """Initialize the service."""
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

    def __init_subclass__(subclass) -> None:  # pylint: disable=bad-classmethod-argument,arguments-differ
        """Make sure subclass has a class variable called 'name'."""
        super().__init_subclass__()
        if inspect.isabstract(subclass):
            return
        for attr in subclass.__annotations__:  # pylint: disable=no-member
            if not hasattr(subclass, attr):
                raise RuntimeError(f"{subclass.__name__} is missing '{attr}' class variable")


class Repository(ABC):
    """Defines the interface for the repository containing computation records."""

    @abstractmethod
    def add(self, comp_rec: ComputationRecord) -> None:
        """Add the given computation record to the repository if it does not already exist."""

    @abstractmethod
    def get(self, identifier: Identifier) -> ComputationRecord:
        """Get the computation record matching the given identifier from the repository if it exists."""

    @abstractmethod
    def __iter__(self) -> Iterator[Identifier]:
        """Iterate over the identifiers of all computation records."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of computation records in the repository."""


class DistributionFinder(ABC):  # pylint: disable=too-few-public-methods
    """Defines the interface for finding distributions."""

    @abstractmethod
    def __call__(self) -> frozenset[Distribution]:
        """Find the distributions installed on the system."""


R = TypeVar("R", bound=Repository)


class UnitOfWork(ABC):
    """Defines the interface for the unit of work."""

    _records: Repository

    def __init__(self) -> None:
        """Initialize the unit of work."""
        self._in_context = False

    @property
    def records(self) -> Repository:
        """Return the records repository if we are currently within the context of the unit of work."""
        if self._in_context:
            return self._records
        raise RuntimeError("Records not available outside of context")

    U = TypeVar("U", bound="UnitOfWork")

    def __enter__(self: U) -> U:
        """Enter the unit of work."""
        self._in_context = True
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        """Exit the unit of work."""
        self.rollback()
        self._in_context = False

    @abstractmethod
    def commit(self) -> None:
        """Commit the unit of work."""

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the unit of work."""
