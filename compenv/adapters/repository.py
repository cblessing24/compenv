"""Contains the DataJoint implementation of the computation record repository."""
from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Iterable, Iterator

from ..model.computation import ComputationRecord, Identifier
from ..model.record import Distribution, InstalledDistributions, Record
from ..service.abstract import Repository
from .abstract import AbstractTableFacade
from .entity import DJComputationRecord, DJDistribution
from .translator import Translator

if TYPE_CHECKING:
    from ..types import PrimaryKey


class DJRepository(Repository):
    """Repository that uses DataJoint tables to persist computation records."""

    def __init__(self, translator: Translator[PrimaryKey], facade: AbstractTableFacade[DJComputationRecord]) -> None:
        """Initialize the computation record repository."""
        self.translator = translator
        self.facade = facade

    def add(self, comp_rec: ComputationRecord) -> None:
        """Add the given computation record to the repository if it does not already exist."""
        primary = self.translator.to_external(comp_rec.identifier)

        try:
            self.facade.add(
                DJComputationRecord(
                    primary=primary,
                    distributions=frozenset(self._persist_dists(comp_rec.record.installed_distributions)),
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
            dj_comp_rec = self.facade.get(primary)
        except KeyError as error:
            raise KeyError(f"Record with identifier '{identifier}' does not exist!") from error

        return ComputationRecord(
            identifier=identifier,
            record=Record(
                installed_distributions=self._reconstitue_installed_dists(dj_comp_rec),
            ),
        )

    def _reconstitue_installed_dists(self, dj_comp_rec: DJComputationRecord) -> InstalledDistributions:
        return InstalledDistributions(self._reconstitue_dist(d) for d in dj_comp_rec.distributions)

    def _reconstitue_dist(self, dj_dist: DJDistribution) -> Distribution:
        return Distribution(
            name=dj_dist.distribution_name,
            version=dj_dist.distribution_version,
        )

    def __iter__(self) -> Iterator[Identifier]:
        """Iterate over the identifiers of all computation records."""
        return (self.translator.to_internal(p) for p in self.facade)

    def __len__(self) -> int:
        """Return the number of computation records in the repository."""
        return len(self.facade)

    def __repr__(self) -> str:
        """Return a string representation of the computation record repository."""
        return f"{self.__class__.__name__}(translator={self.translator}, facade={self.facade})"
