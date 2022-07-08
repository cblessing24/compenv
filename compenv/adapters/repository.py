"""Contains the DataJoint implementation of the computation record repository."""
from pathlib import Path
from typing import Generator, Iterable, Iterator

from ..model.computation import ComputationRecord, Identifier
from ..model.record import ActiveModules, Distribution, InstalledDistributions, Module, Modules, Record
from ..service.abstract import Repository
from .abstract import AbstractTableFacade
from .entity import DJComputationRecord, DJDistribution, DJMembership, DJModule
from .translator import DJTranslator


class DJRepository(Repository):
    """Repository that uses DataJoint tables to persist computation records."""

    def __init__(self, translator: DJTranslator, facade: AbstractTableFacade[DJComputationRecord]) -> None:
        """Initialize the computation record repository."""
        self.translator = translator
        self.facade = facade

    def __setitem__(self, identifier: Identifier, comp_rec: ComputationRecord) -> None:
        """Add the given computation record to the repository if it does not already exist."""
        primary = self.translator.to_primary(identifier)

        try:
            self.facade[primary] = DJComputationRecord(
                modules=frozenset(self._persist_modules(comp_rec.record.modules)),
                distributions=frozenset(self._persist_dists(comp_rec.record.installed_distributions)),
                memberships=frozenset(self._get_memberships(comp_rec.record.installed_distributions)),
            )
        except ValueError as error:
            raise ValueError(f"Record with identifier '{identifier}' already exists!") from error

    @staticmethod
    def _persist_modules(modules: Iterable[Module]) -> Generator[DJModule, None, None]:
        for module in modules:
            yield DJModule(module_file=str(module.file), module_is_active="True" if module.is_active else "False")

    @staticmethod
    def _persist_dists(dists: Iterable[Distribution]) -> Generator[DJDistribution, None, None]:
        for dist in dists:
            yield DJDistribution(distribution_name=dist.name, distribution_version=dist.version)

    @staticmethod
    def _get_memberships(dists: Iterable[Distribution]) -> Generator[DJMembership, None, None]:
        for dist in dists:
            for module in dist.modules:
                yield DJMembership(
                    distribution_name=dist.name, distribution_version=dist.version, module_file=str(module.file)
                )

    def __delitem__(self, identifier: Identifier) -> None:
        """Remove the computation record matching the given identifier from the repository if it exists."""
        primary = self.translator.to_primary(identifier)

        try:
            del self.facade[primary]
        except KeyError as error:
            raise KeyError(f"Record with identifier '{identifier}' does not exist!") from error

    def __getitem__(self, identifier: Identifier) -> ComputationRecord:
        """Get the computation record matching the given identifier from the repository if it exists."""
        primary = self.translator.to_primary(identifier)

        try:
            dj_comp_rec = self.facade[primary]
        except KeyError as error:
            raise KeyError(f"Record with identifier '{identifier}' does not exist!") from error

        return ComputationRecord(
            identifier=identifier,
            record=Record(
                installed_distributions=self._reconstitue_installed_dists(dj_comp_rec),
                active_modules=self._reconstitute_active_modules(dj_comp_rec.modules),
            ),
        )

    def _reconstitue_installed_dists(self, dj_comp_rec: DJComputationRecord) -> InstalledDistributions:
        return InstalledDistributions(
            self._reconstitue_dist(d, self._filter_dj_modules(d, dj_comp_rec.modules, dj_comp_rec.memberships))
            for d in dj_comp_rec.distributions
        )

    def _filter_dj_modules(
        self, dj_dist: DJDistribution, dj_modules: Iterable[DJModule], dj_memberships: Iterable[DJMembership]
    ) -> Generator[DJModule, None, None]:
        for dj_membership in self._filter_dj_memberships(dj_dist, dj_memberships):
            try:
                yield next(m for m in dj_modules if m.module_file == dj_membership.module_file)
            except StopIteration as error:
                raise ValueError(f"Module referenced in membership '{dj_membership}' does not exist!") from error

    @staticmethod
    def _filter_dj_memberships(
        dj_dist: DJDistribution, dj_memberships: Iterable[DJMembership]
    ) -> Generator[DJMembership, None, None]:
        return (
            a
            for a in dj_memberships
            if a.distribution_name == dj_dist.distribution_name
            and a.distribution_version == dj_dist.distribution_version
        )

    def _reconstitue_dist(self, dj_dist: DJDistribution, dj_modules: Iterable[DJModule]) -> Distribution:
        return Distribution(
            name=dj_dist.distribution_name,
            version=dj_dist.distribution_version,
            modules=self._reconstitute_modules(dj_modules),
        )

    def _reconstitute_active_modules(self, dj_modules: Iterable[DJModule]) -> ActiveModules:
        return ActiveModules(self._reconstitute_modules(m for m in dj_modules if m.module_is_active == "True"))

    def _reconstitute_modules(self, modules: Iterable[DJModule]) -> Modules:
        return Modules(self._reconstitute_module(m) for m in modules)

    @staticmethod
    def _reconstitute_module(module: DJModule) -> Module:
        return Module(file=Path(module.module_file), is_active=module.module_is_active == "True")

    def __iter__(self) -> Iterator[Identifier]:
        """Iterate over the identifiers of all computation records."""
        return (self.translator.to_identifier(p) for p in self.facade)

    def __len__(self) -> int:
        """Return the number of computation records in the repository."""
        return len(self.facade)

    def __repr__(self) -> str:
        """Return a string representation of the computation record repository."""
        return f"{self.__class__.__name__}(translator={self.translator}, facade={self.facade})"
