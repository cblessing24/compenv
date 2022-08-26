"""Contains the diff service."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..model.record import Identifier
from ..service import register_service_class
from .abstract import Repository, Request, Response, Service


@dataclass(frozen=True)
class DiffRequest(Request):
    """Request expected by the diff service."""

    identifier1: Identifier
    identifier2: Identifier


@dataclass(frozen=True)
class DiffResponse(Response):
    """Response returned by the diff service."""

    differ: bool


@register_service_class
class DiffService(Service[DiffRequest, DiffResponse]):  # pylint: disable=too-few-public-methods
    """A service used to get a diff between two computation records."""

    name = "diff"

    def __init__(self, *, output_port: Callable[[DiffResponse], None], repo: Repository) -> None:
        """Initialize the service."""
        super().__init__(output_port=output_port)
        self.repo = repo

    def _execute(self, request: DiffRequest) -> DiffResponse:
        """Determine the diff of two computation records."""
        rec1 = self.repo.get(request.identifier1)
        rec2 = self.repo.get(request.identifier2)
        return DiffResponse(differ=rec1.distributions != rec2.distributions)
