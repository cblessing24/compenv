from typing import Any, Dict, Iterator, Mapping, Union

PrimaryKey = Dict[str, Union[str, float, int]]

class Table:
    def insert1(self, row: Mapping[str, Any]) -> None: ...
    def delete_quick(self) -> None: ...
    def __contains__(self, other: object) -> bool: ...
    def __and__(self, restriction: PrimaryKey) -> Table: ...
    def __iter__(self) -> Iterator[PrimaryKey]: ...
    def __len__(self) -> int: ...

class AutoPopulatedTable(Table):
    def make(self, key: PrimaryKey) -> None: ...

class Lookup(Table): ...
class Part(Table): ...