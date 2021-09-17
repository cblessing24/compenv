"""Contains DataJoint entities."""
from __future__ import annotations

import dataclasses
from typing import Any, ClassVar, FrozenSet, List, Literal, Mapping, Type

from .abstract import MasterEntity, PartEntity


@dataclasses.dataclass(frozen=True)
class Module(PartEntity):
    """DataJoint entity representing a module."""

    master_attr = "modules"

    definition = """
    -> master
    module_file: varchar(256)
    ---
    module_is_active: enum("True", "False")
    """

    module_file: str
    module_is_active: Literal["True", "False"]

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> Module:
        """Create a module from the given mapping."""
        return cls(mapping["module_file"], mapping["module_is_active"])


DJModule = Module


@dataclasses.dataclass(frozen=True)
class Distribution(PartEntity):
    """DataJoint entity representing a distribution."""

    master_attr = "distributions"

    definition = """
    -> master
    distribution_name: varchar(64)
    distribution_version: varchar(128)
    """

    distribution_name: str
    distribution_version: str

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> Distribution:
        """Create a distribution from the given mapping."""
        return cls(mapping["distribution_name"], mapping["distribution_version"])


DJDistribution = Distribution


@dataclasses.dataclass(frozen=True)
class Membership(PartEntity):
    """DataJoint entity representing the membership of a given module in a distribution."""

    master_attr = "memberships"

    definition = """
    -> master.Module
    -> master.Distribution
    """

    module_file: str
    distribution_name: str
    distribution_version: str

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> Membership:
        """Create a membership from the given mapping."""
        return cls(mapping["module_file"], mapping["distribution_name"], mapping["distribution_version"])


DJMembership = Membership


@dataclasses.dataclass(frozen=True)
class ComputationRecord(MasterEntity):
    """DataJoint entity representing a computation record."""

    parts: ClassVar[List[Type[PartEntity]]] = [Module, Distribution, Membership]

    modules: FrozenSet[Module]
    distributions: FrozenSet[Distribution]
    memberships: FrozenSet[Membership]


DJComputationRecord = ComputationRecord
