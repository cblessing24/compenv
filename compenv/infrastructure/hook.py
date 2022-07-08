"""Contains code related to hooks."""
from typing import TYPE_CHECKING, Callable, Type, TypeVar

if TYPE_CHECKING:
    from datajoint.table import AutoPopulatedTable, PrimaryKey

    _T = TypeVar("_T", bound=AutoPopulatedTable)

    AutoPopulatedTableDecorator = Callable[[Type[_T]], Type[_T]]
    MakeMethod = Callable[[_T, PrimaryKey], None]


def hook_into_make_method(
    hook: "Callable[[MakeMethod[_T], _T, PrimaryKey], None]",
) -> "AutoPopulatedTableDecorator[_T]":
    """Give control over the execution of a table's make method to a callable hook.

    This function is meant to be used as a decorator. It will modify the make method of the decorated table. Calling
    the modified make method will call the hook that was passed into the decorator with a reference to the original make
    method, the table instance and the key. The original make method can the be executed by calling it with the table
    instance and the key. This allows the execution of arbitrary code before and after the original make method.
    """

    def _hook_into_make_method(table_cls: "Type[_T]") -> "Type[_T]":
        original_make_method = table_cls.make

        def hooked_make_method(self: "_T", key: "PrimaryKey") -> None:
            hook(original_make_method, self, key)

        setattr(table_cls, "make", hooked_make_method)
        return table_cls

    return _hook_into_make_method
