from typing import Protocol

from .table import PrimaryKey

class SupportsAutoPopulate(Protocol):
    def make(self, key: PrimaryKey) -> None: ...
