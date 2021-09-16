"""Contains DataJoint entities."""
import dataclasses
from typing import FrozenSet, Literal

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


DJMembership = Membership


@dataclasses.dataclass(frozen=True)
class ComputationRecord(MasterEntity):
    """DataJoint entity representing a computation record."""

    parts = [Module, Distribution, Membership]

    modules: FrozenSet[Module]
    distributions: FrozenSet[Distribution]
    memberships: FrozenSet[Membership]


DJComputationRecord = ComputationRecord
