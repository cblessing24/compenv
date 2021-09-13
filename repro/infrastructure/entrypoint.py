"""Contains entrypoints to the application."""

import functools
from types import FrameType
from typing import Callable, Optional, Type, TypeVar

from datajoint.autopopulate import AutoPopulate
from datajoint.schemas import Schema

from ..adapters.repository import DJCompRecRepo
from ..adapters.translator import DJTranslator, PrimaryKey, blake2b
from ..service import record
from .facade import RecordTableFacade
from .factory import RecordTableFactory
from .hook import hook_into_make_method

_T = TypeVar("_T", bound=AutoPopulate)


class EnvironmentRecorder:  # pylint: disable=too-few-public-methods
    """Records the environment."""

    def __init__(self, get_current_frame: Callable[[], Optional[FrameType]]) -> None:
        """Initialize the environment recorder."""
        self.get_current_frame = get_current_frame

    def __call__(self, schema: Schema) -> Callable[[Type[_T]], Type[_T]]:
        """Record the environment during executions of the table's make method."""

        def _record_environment(table_cls: Type[_T]) -> Type[_T]:
            if not schema.context:
                curr_frame = self.get_current_frame()
                if not curr_frame:
                    raise RuntimeError("Need stack frame support to dynamically determine context!")
                prev_frame = curr_frame.f_back
                if not prev_frame:
                    raise RuntimeError("No previous stack frame found but needed to dynamically determine context!")
                schema.context = prev_frame.f_locals
            table_cls = schema(table_cls)

            factory = RecordTableFactory(schema, parent=table_cls)
            translator = DJTranslator(blake2b)
            repo = DJCompRecRepo(facade=RecordTableFacade(factory), translator=translator)

            def hook(trigger: Callable[[PrimaryKey], None], table_cls: _T, key: PrimaryKey) -> None:
                identifier = translator.to_identifier(key)
                record.record(repo, trigger=functools.partial(trigger, table_cls, key), identifier=identifier)

            table_cls = hook_into_make_method(hook)(table_cls)
            table_cls.records = factory

            return table_cls

        return _record_environment
