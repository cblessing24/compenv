"""Contains entrypoints to the application."""
from __future__ import annotations

import functools
import inspect
from collections.abc import Generator
from contextlib import contextmanager
from typing import Callable, Mapping, Optional, Type, TypeVar

from ..adapters.controller import DJController
from ..backend import create_dj_backend
from ..types import PrimaryKey
from . import types
from .hook import hook_into_make_method


class Entrypoint:  # pylint: disable=too-few-public-methods
    """Entrypoint to most services."""

    def __init__(self, controller: DJController):
        """Initialize the entrypoint."""
        self.controller = controller

    def diff(self, key1: PrimaryKey, key2: PrimaryKey) -> None:
        """Show a diff between two records."""
        self.controller.diff(key1, key2)


_T = TypeVar("_T", bound=types.AutopopulatedTable)


DEFAULT_GET_CURRENT_FRAME = inspect.currentframe


def determine_context(context: Mapping[str, object], current_frame: Optional[types.FrameType]) -> dict[str, object]:
    """Determine the context."""
    if context:
        return dict(context)
    if not current_frame:
        raise RuntimeError("Need stack frame support to dynamically determine context!")
    prev_frame = current_frame.f_back
    if not prev_frame:
        raise RuntimeError("No previous stack frame found but needed to dynamically determine context!")
    return dict(prev_frame.f_locals)


@contextmanager
def replaced_connection_table(table: _T, replacement_connection: types.Connection) -> Generator[_T, None, None]:
    """Replace the connection of the given table with the given connection within the context."""
    table_cls = table.__class__
    original_connection = table_cls.connection
    table_cls.connection = replacement_connection
    try:
        yield table_cls()
    finally:
        table_cls.connection = original_connection


class EnvironmentRecorder:  # pylint: disable=too-few-public-methods
    """Records the environment."""

    def __init__(self, get_current_frame: Callable[[], Optional[types.FrameType]] = DEFAULT_GET_CURRENT_FRAME) -> None:
        """Initialize the environment recorder."""
        self.get_current_frame = get_current_frame

    def __call__(self, schema: types.Schema) -> Callable[[Type[_T]], Type[_T]]:
        """Record the environment during executions of the table's make method."""

        def _record_environment(table_cls: Type[_T]) -> Type[_T]:
            schema.context = determine_context(schema.context, self.get_current_frame())
            table_cls = schema(table_cls)
            backend = create_dj_backend(schema, table_cls.__name__)
            with backend.infra.connection:
                backend.infra.factory()
            self._modify_table(table_cls, backend.adapters.controller)
            return table_cls

        return _record_environment

    @staticmethod
    def _modify_table(table_cls: Type[_T], controller: DJController) -> None:
        def hook(make: Callable[[_T, types.Entity], None], table: _T, key: types.Entity) -> None:
            controller.record(key, functools.partial(make, table))

        table_cls = hook_into_make_method(hook)(table_cls)
        setattr(table_cls, "records", Entrypoint(controller))
