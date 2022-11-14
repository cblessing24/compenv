"""Contains the DataJoint implementation of the computation record repository."""
from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Iterable, Iterator

from ..model.computation import AlgorithmName, Computation, ComputationRegistry, ComputationRegistryRepository
from ..model.record import ComputationRecord, Distribution, Identifier
from ..service.abstract import Repository
from .abstract import AbstractTable
from .entity import DJComputationRecord, DJDistribution
from .translator import Translator

if TYPE_CHECKING:
    from ..types import PrimaryKey


class DJRepository(Repository):
    """Repository that uses DataJoint tables to persist computation records."""

    def __init__(self, translator: Translator[PrimaryKey], table: AbstractTable[DJComputationRecord]) -> None:
        """Initialize the computation record repository."""
        self.translator = translator
        self.table = table

    def add(self, comp_rec: ComputationRecord) -> None:
        """Add the given computation record to the repository if it does not already exist."""
        primary = self.translator.to_external(comp_rec.identifier)

        try:
            self.table.add(
                DJComputationRecord(
                    primary=primary,
                    distributions=frozenset(self._persist_dists(comp_rec.distributions)),
                ),
            )
        except ValueError as error:
            raise ValueError(f"Record with identifier '{comp_rec.identifier}' already exists!") from error

    @staticmethod
    def _persist_dists(dists: Iterable[Distribution]) -> Generator[DJDistribution, None, None]:
        for dist in dists:
            yield DJDistribution(distribution_name=dist.name, distribution_version=dist.version)

    def get(self, identifier: Identifier) -> ComputationRecord:
        """Get the computation record matching the given identifier from the repository if it exists."""
        primary = self.translator.to_external(identifier)

        try:
            dj_comp_rec = self.table.get(primary)
        except KeyError as error:
            raise KeyError(f"Record with identifier '{identifier}' does not exist!") from error

        return ComputationRecord(
            identifier=identifier,
            distributions=self._reconstitue_distributions(dj_comp_rec),
        )

    def _reconstitue_distributions(self, dj_comp_rec: DJComputationRecord) -> frozenset[Distribution]:
        return frozenset(self._reconstitue_dist(d) for d in dj_comp_rec.distributions)

    def _reconstitue_dist(self, dj_dist: DJDistribution) -> Distribution:
        return Distribution(
            name=dj_dist.distribution_name,
            version=dj_dist.distribution_version,
        )

    def __iter__(self) -> Iterator[Identifier]:
        """Iterate over the identifiers of all computation records."""
        return (self.translator.to_internal(p) for p in self.table)

    def __len__(self) -> int:
        """Return the number of computation records in the repository."""
        return len(self.table)

    def __repr__(self) -> str:
        """Return a string representation of the computation record repository."""
        return f"{self.__class__.__name__}(translator={self.translator}, table={self.table})"


class DJComputationRegistryRepository(ComputationRegistryRepository):
    """Repository that uses DataJoint tables to persist computation registries."""

    def add(self, registry: ComputationRegistry) -> None:
        """Add a registry to the repository."""
        # 1. Persist registry
        # 2. Track registry using tracker

    def get(self, algorithm_name: AlgorithmName) -> ComputationRegistry:
        """Get the registry for the given algorithm name."""
        # 1. Reconstitute registry from tables
        # 2. Track registry using tracker
        # 3. Return registry

    def flush(self) -> None:
        """Persist changes made to registries managed by this repository."""
        # 1. Get changes from tracker
        # 2. Persist changes
        # 3. Clear tracker


class ComputationRegistryTracker:
    """Tracker that tracks changes made to computation registries."""

    def track(self, registry: ComputationRegistry) -> None:
        """Track changes made to the given registry."""
        # 1. Create copy of registry
        # 2. Add copy to mapping of original to copy

    @property
    def changes(self) -> Iterator[Computation]:
        """Return the changes made to tracked repositories."""
        # Changes:
        #  * Added computations: original.computations - copy.computations
        #  * Removed computations: copy.computations - original.computations

    def clear(self) -> None:
        """Clear any tracked changes."""
        # 1. Replace copies with originals in mapping
