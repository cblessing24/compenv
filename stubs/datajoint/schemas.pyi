from typing import Any, Dict, Optional, Type, TypeVar

from .table import Table

_Context = Dict[str, Any]
_V = TypeVar("_V", bound=Table)

class Schema:
    context: Dict[str, Any]
    def __init__(self, schema_name: str, context: Optional[_Context] = ...) -> None: ...
    def spawn_missing_classes(self, context: Optional[_Context] = ...) -> None: ...
    def __call__(self, cls: Type[_V], *, context: Optional[_Context] = ...) -> Type[_V]: ...
