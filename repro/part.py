"""Contains code for working with DataJoint part tables."""
from typing import Callable

from datajoint import Part, Table


def add_part_table(name: str, definition: str) -> Callable[[Table], Table]:
    """Add a part table with the specified name and definition to the decorated table."""

    def _add_part_table(table_cls: Table) -> Table:
        part_table = type(name, (Part,), {"definition": definition})
        setattr(table_cls, name, part_table)
        return table_cls

    return _add_part_table
