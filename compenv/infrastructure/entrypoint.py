"""Contains entrypoints to the application."""
from __future__ import annotations

import functools
import inspect
from types import FrameType
from typing import Callable, Optional, Type, TypeVar

from ..adapters.controller import DJController
from ..backend import create_dj_backend
from .hook import hook_into_make_method
from .types import AutopopulatedTable, Entity, Schema

_T = TypeVar("_T", bound=AutopopulatedTable)


DEFAULT_GET_CURRENT_FRAME = inspect.currentframe


class EnvironmentRecorder:  # pylint: disable=too-few-public-methods
    """Records the environment."""

    def __init__(
        self,
        get_current_frame: Callable[[], Optional[FrameType]] = DEFAULT_GET_CURRENT_FRAME,
    ) -> None:
        """Initialize the environment recorder."""
        self.get_current_frame = get_current_frame

    def __call__(self, schema: Schema) -> Callable[[Type[_T]], Type[_T]]:
        """Record the environment during executions of the table's make method."""

        def _record_environment(table_cls: Type[_T]) -> Type[_T]:
            if not schema.context:
                schema.context = self._determine_context(self.get_current_frame())
            backend = create_dj_backend(schema, table_cls.__name__)
            self._modify_table(schema, table_cls, backend.adapters.controller)

            # Create record table now while not in a transaction.
            backend.infra.factory()

            return table_cls

        return _record_environment

    def _determine_context(self, current_frame: Optional[FrameType]) -> dict[str, object]:
        if not current_frame:
            raise RuntimeError("Need stack frame support to dynamically determine context!")
        prev_frame = current_frame.f_back
        if not prev_frame:
            raise RuntimeError("No previous stack frame found but needed to dynamically determine context!")
        return prev_frame.f_locals

    @staticmethod
    def _modify_table(schema: Schema, table_cls: Type[_T], controller: DJController) -> None:
        def hook(make: Callable[[_T, Entity], None], table: _T, key: Entity) -> None:
            controller.record(key, functools.partial(make, table))

        table_cls = schema(table_cls)
        table_cls = hook_into_make_method(hook)(table_cls)
