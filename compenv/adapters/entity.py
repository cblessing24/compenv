"""Contains DataJoint entities."""
from __future__ import annotations

import dataclasses
from typing import Any, ClassVar, FrozenSet, List, Mapping, Type

from .abstract import MasterEntity, PartEntity


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
class ComputationRecord(MasterEntity):
    """DataJoint entity representing a computation record."""

    parts: ClassVar[List[Type[PartEntity]]] = [Distribution]

    distributions: FrozenSet[Distribution]


DJComputationRecord = ComputationRecord
