"""Contains code related to the dynamic creation of tables."""
from functools import lru_cache
from typing import Dict, Type

from datajoint.autopopulate import AutoPopulate
from datajoint.schemas import Schema
from datajoint.table import Table
from datajoint.user_tables import Lookup, Part

from ..adapters.abstract import PartEntity


class RecordTableFactory:
    """Produces record table instances."""

    def __init__(self, schema: Schema, parent: str) -> None:
        """Initialize the factory."""
        self.schema = schema
        self.parent = parent
        self()

    @lru_cache(maxsize=None)
    def __call__(self) -> Table:
        """Produce a record table instance."""
        master_cls = type(self.parent + "Record", (Lookup,), {"definition": "-> " + self.parent})
        for part_cls in PartEntity.__subclasses__():
            setattr(
                master_cls,
                part_cls.__name__,
                type(part_cls.__name__, (Part,), {"definition": part_cls.definition}),
            )
        schema_tables: Dict[str, Type[AutoPopulate]] = {}
        self.schema.spawn_missing_classes(schema_tables)
        context = {self.parent: schema_tables[self.parent]}
        if self.schema.context:
            context.update(self.schema.context)
        return self.schema(master_cls, context=context)()

    def __repr__(self) -> str:
        """Create a string representation of the factory."""
        return f"{self.__class__.__name__}(schema={repr(self.schema)}, parent={repr(self.parent)})"
