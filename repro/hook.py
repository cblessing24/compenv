"""Contains code related to hooks."""
from typing import Callable, Mapping, Union

from datajoint.table import Table

Key = Mapping[str, Union[int, str]]
MakeMethod = Callable[[Table, Key], None]


class MakeMethodHookInstaller:
    """A class decorator for imported/computed DataJoint tables that installs hooks in the table's make method."""

    def __init__(self, pre_hook: MakeMethod, post_hook: MakeMethod) -> None:
        """Initialize the make method hook installer."""
        self.pre_hook = pre_hook
        self.post_hook = post_hook

    def __call__(self, table_cls: Table) -> Table:
        """Replace the make method with a "hooked" version."""
        table_cls.make = self._create_hooked_make_method(table_cls.make)
        return table_cls

    def _create_hooked_make_method(self, make_method: MakeMethod) -> MakeMethod:
        """Create a "hooked" version of the passed in make method by inserting a hook before and after it."""

        def hooked_make_method(table: Table, key: Key) -> None:
            """Call the pre hook first, then the make method and lastly the post hook."""
            self.pre_hook(table, key)
            make_method(table, key)
            self.post_hook(table, key)

        return hooked_make_method

    def __repr__(self) -> str:
        """Return a string representation of the class."""
        return f"{self.__class__.__name__}(pre_hook={self.pre_hook}, post_hook={self.post_hook})"
