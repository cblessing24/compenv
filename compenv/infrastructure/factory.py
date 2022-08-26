"""Contains code related to the dynamic creation of tables."""
from __future__ import annotations

from functools import lru_cache
from typing import Dict, Type

from datajoint import Lookup, Part

from ..adapters.abstract import PartEntity
from .types import Schema


class DJTableFactory:
    """Produces record table instances."""

    def __init__(self, schema: Schema, parent: str) -> None:
        """Initialize the factory."""
        self.schema = schema
        self.parent = parent

    @lru_cache
    def __call__(self) -> Lookup:
        """Produce a record table instance."""
        master_cls: Type[Lookup] = type(self.parent + "Record", (Lookup,), {"definition": "-> " + self.parent})
        for part_cls in PartEntity.__subclasses__():
            setattr(
                master_cls,
                part_cls.__name__,
                type(part_cls.__name__, (Part,), {"definition": part_cls.definition}),
            )
        schema_tables: Dict[str, object] = {}
        self.schema.spawn_missing_classes(schema_tables)
        context: dict[str, object] = {self.parent: schema_tables[self.parent]}
        if self.schema.context:
            context.update(self.schema.context)
        return self.schema(master_cls, context=context)()

    def __repr__(self) -> str:
        """Create a string representation of the factory."""
        return f"{self.__class__.__name__}(schema={repr(self.schema)}, parent={repr(self.parent)})"
