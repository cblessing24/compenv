"""Contains code related to hooks."""
from typing import Callable, Mapping, Type, TypeVar, Union

from datajoint.table import Table

Key = Mapping[str, Union[int, str]]
MakeMethod = Callable[[Table, Key], None]


TableTypeVar = TypeVar("TableTypeVar", bound=Table)


def add_hooks_to_make_method(
    pre_hook: MakeMethod, post_hook: MakeMethod
) -> Callable[[Type[TableTypeVar]], Type[TableTypeVar]]:
    """Add a hook before and after the decorated table's make method."""

    def _add_hooks_to_make_method(table_cls: Type[TableTypeVar]) -> Type[TableTypeVar]:
        original_make_method = table_cls.make

        def make_method_with_hooks(table: TableTypeVar, key: Key) -> None:
            pre_hook(table, key)
            original_make_method(table, key)
            post_hook(table, key)

        table_cls.make = make_method_with_hooks
        return table_cls

    return _add_hooks_to_make_method
