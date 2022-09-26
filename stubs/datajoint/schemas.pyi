from typing import Any, Dict, Mapping, MutableMapping, Optional, Type, TypeVar

from .connection import Connection
from .table import Table

Context = MutableMapping[str, Any]
_V = TypeVar("_V", bound=Table)

class Schema:
    context: Dict[str, object]
    connection: Connection
    database: str
    def __init__(
        self, schema_name: str, context: Optional[Context] = ..., *, connection: Optional[Connection] = None
    ) -> None: ...
    def spawn_missing_classes(self, context: Optional[Context] = ...) -> None: ...
    def __call__(self, cls: Type[_V], *, context: Optional[Mapping[str, object]] = ...) -> Type[_V]: ...
