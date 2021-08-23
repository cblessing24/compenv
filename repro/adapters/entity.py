import dataclasses
from typing import Literal

from .abstract import DJMasterEntity, DJPartEntity


@dataclasses.dataclass(frozen=True)
class Module(DJPartEntity):
    """DataJoint entity representing a module."""

    master_attr = "modules"

    definition = """
    module_file: varchar(64)
    ---
    module_is_active: enum("True", "False")
    """

    module_file: str
    module_is_active: Literal["True", "False"]


DJModule = Module


@dataclasses.dataclass(frozen=True)
class Distribution(DJPartEntity):
    """DataJoint entity representing a distribution."""

    master_attr = "distributions"

    definition = """
    distribution_name: varchar(64)
    ---
    distribution_version: varchar(64)
    """

    distribution_name: str
    distribution_version: str


DJDistribution = Distribution


@dataclasses.dataclass(frozen=True)
class ModuleAffiliation(DJPartEntity):
    """DataJoint entity representing the affiliation of a given module to a distribution."""

    master_attr = "module_affiliations"

    definition = """
    -> Module
    -> Distribution
    """

    module_file: str
    distribution_name: str


DJModuleAffiliation = ModuleAffiliation


@dataclasses.dataclass(frozen=True)
class ComputationRecord(DJMasterEntity):
    """DataJoint entity representing a computation record."""

    parts = [Module, Distribution, ModuleAffiliation]

    modules: frozenset[Module]
    distributions: frozenset[Distribution]
    module_affiliations: frozenset[ModuleAffiliation]


DJComputationRecord = ComputationRecord
