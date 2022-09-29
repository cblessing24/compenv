"""Contains entrypoints to the application."""
from __future__ import annotations

import functools
import inspect
from typing import Callable, Mapping, Optional, Type, TypeVar

from ..adapters.controller import DJController
from ..backend import create_dj_backend
from ..types import PrimaryKey
from .hook import hook_into_make_method
from .types import AutopopulatedTable, Entity, FrameType, Schema


class Entrypoint:  # pylint: disable=too-few-public-methods
    """Entrypoint to most services."""

    def __init__(self, controller: DJController):
        """Initialize the entrypoint."""
        self.controller = controller

    def diff(self, key1: PrimaryKey, key2: PrimaryKey) -> None:
        """Show a diff between two records."""
        self.controller.diff(key1, key2)


_T = TypeVar("_T", bound=AutopopulatedTable)


DEFAULT_GET_CURRENT_FRAME = inspect.currentframe


def determine_context(context: Mapping[str, object], current_frame: Optional[FrameType]) -> dict[str, object]:
    """Determine the context."""
    if context:
        return dict(context)
    if not current_frame:
        raise RuntimeError("Need stack frame support to dynamically determine context!")
    prev_frame = current_frame.f_back
    if not prev_frame:
        raise RuntimeError("No previous stack frame found but needed to dynamically determine context!")
    return dict(prev_frame.f_locals)


class EnvironmentRecorder:  # pylint: disable=too-few-public-methods
    """Records the environment."""

    def __init__(self, get_current_frame: Callable[[], Optional[FrameType]] = DEFAULT_GET_CURRENT_FRAME) -> None:
        """Initialize the environment recorder."""
        self.get_current_frame = get_current_frame

    def __call__(self, schema: Schema) -> Callable[[Type[_T]], Type[_T]]:
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
        def hook(make: Callable[[_T, Entity], None], table: _T, key: Entity) -> None:
            controller.record(key, functools.partial(make, table))

        table_cls = hook_into_make_method(hook)(table_cls)
        setattr(table_cls, "records", Entrypoint(controller))
