"""Contains code related to the dynamic creation of tables."""
from abc import ABC, abstractmethod
from functools import cache
from typing import Type

from datajoint.schemas import Schema
from datajoint.table import Table
from datajoint.user_tables import Lookup, Part


class PartSpec(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for all part table specifications."""

    definition: str


class Module(PartSpec):  # pylint: disable=too-few-public-methods
    """Specification for a part table holding information about modules."""

    definition = """
    module_file: varchar(64)
    ---
    module_is_active: enum("True", "False")
    """


class Distribution(PartSpec):  # pylint: disable=too-few-public-methods
    """Specification for a part table holding information about distributions."""

    definition = """
    distribution_name: varchar(64)
    ---
    distribution_version: varchar(64)
    """


class ModuleAffiliation(PartSpec):  # pylint: disable=too-few-public-methods
    """Specification for a part table holding information about module affiliations."""

    definition = """
    -> Module
    -> Distribution
    """


PARTS: list[Type[PartSpec]] = [Module, Distribution, ModuleAffiliation]


class RecordTableFactory:
    """Produces record table instances."""

    def __init__(self, schema: Schema, parent: str) -> None:
        """Initialize the factory."""
        self.schema = schema
        self.parent = parent

    @cache
    def __call__(self) -> Table:
        """Produce a record table instance."""
        master_cls = type("Record", (Lookup,), {"definition": "-> " + self.parent})
        for part_cls in PARTS:
            setattr(
                master_cls,
                part_cls.__name__,
                type(part_cls.__name__, (Part,), {"definition": "-> master\n" + part_cls.definition}),
            )
        return self.schema(master_cls)()

    def __repr__(self) -> str:
        """Create a string representation of the factory."""
        return f"{self.__class__.__name__}(schema={repr(self.schema)}, parent='{self.parent}')"
