"""Contains entrypoints to the application."""

import functools
from typing import Callable, Type, TypeVar

from datajoint.autopopulate import AutoPopulate

from ..adapters.repository import DJCompRecRepo
from ..adapters.translator import DJTranslator, PrimaryKey, blake2b
from ..service import record
from .facade import RecordTableFacade
from .factory import RecordTableFactory
from .hook import hook_into_make_method

_T = TypeVar("_T", bound=AutoPopulate)


def record_environment(table_cls: Type[_T]) -> Type[_T]:
    """Record the environment during executions of the table's make method."""
    if not hasattr(table_cls, "database"):
        raise ValueError("Schema decorator must be applied before applying this decorator!")

    schema = table_cls.connection.schemas[table_cls.database]
    factory = RecordTableFactory(schema, parent=table_cls.__name__)
    translator = DJTranslator(blake2b)
    repo = DJCompRecRepo(facade=RecordTableFacade(factory), translator=translator)

    def hook(trigger: Callable[[PrimaryKey], None], table_cls: _T, key: PrimaryKey) -> None:
        identifier = translator.to_identifier(key)
        record.record(repo, trigger=functools.partial(trigger, table_cls, key), identifier=identifier)

    table_cls = hook_into_make_method(hook)(table_cls)
    table_cls.records = factory

    return table_cls
