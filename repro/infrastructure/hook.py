"""Contains code related to hooks."""
from typing import Callable, Type, TypeVar

from datajoint.table import Table

from ..adapters.translator import PrimaryKey

TableTypeVar = TypeVar("TableTypeVar", bound=Table)


def hook_into_make_method(
    hook: Callable[[Callable[[PrimaryKey], None], Table, PrimaryKey], None]
) -> Callable[[Type[TableTypeVar]], Type[TableTypeVar]]:
    """Give control over the execution of a table's make method to a callable hook.

    This function is meant to be used as a decorator. It will modify the make method of the decorated table. Calling
    the modified make method will call the hook that was passed into the decorator with a reference to the original make
    method, the table instance and the key. The original make method can the be executed by calling it with the table
    instance and the key. This allows the execution of arbitrary code before and after the original make method.
    """

    def _hook_into_make_method(table_cls: Type[TableTypeVar]) -> Type[TableTypeVar]:
        original_make_method = table_cls.make

        def hooked_make_method(table: TableTypeVar, key: PrimaryKey) -> None:
            hook(original_make_method, table, key)

        table_cls.make = hooked_make_method
        return table_cls

    return _hook_into_make_method
