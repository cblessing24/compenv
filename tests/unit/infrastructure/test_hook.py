from __future__ import annotations

from typing import Callable

from compenv.infrastructure.hook import hook_into_make_method
from compenv.infrastructure.types import Entity

from ..conftest import FakeAutopopulatedTable


class Hook:
    def __call__(
        self,
        original_make_method: Callable[[FakeAutopopulatedTable, Entity], None],
        table: FakeAutopopulatedTable,
        key: Entity,
    ) -> None:
        original_make_method(table, key)


def test_if_hook_gets_called_with_correct_arguments() -> None:
    table_cls = hook_into_make_method(Hook())(FakeAutopopulatedTable)
    table = table_cls()
    table.make({"a": 1})
    assert table.key == {"a": 1}
