"""Contains repository code."""
import dataclasses
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, Iterable, Literal

from ..model.computation import ComputationRecord, Identifier
from ..model.record import ActiveModules, Distribution, InstalledDistributions, Module, Modules, Record
from .abstract import AbstractTableFacade, DJMasterEntity, DJPartEntity
from .translator import DataJointTranslator


@dataclasses.dataclass(frozen=True)
class DJModule(DJPartEntity):
    """DataJoint entity representing a module."""

    part_table = "Module"
    master_attr = "modules"

    module_file: str
    module_is_active: Literal["True", "False"]


@dataclasses.dataclass(frozen=True)
class DJDistribution(DJPartEntity):
    """DataJoint entity representing a distribution."""

    part_table = "Distribution"
    master_attr = "distributions"

    distribution_name: str
    distribution_version: str


@dataclasses.dataclass(frozen=True)
class DJModuleAffiliation(DJPartEntity):
    """DataJoint entity representing the affiliation of a given module to a distribution."""

    part_table = "ModuleAffiliation"
    master_attr = "module_affiliations"

    module_file: str
    distribution_name: str


@dataclasses.dataclass(frozen=True)
class DJComputationRecord(DJMasterEntity):
    """DataJoint entity representing a computation record."""

    parts = [DJModule, DJDistribution, DJModuleAffiliation]

    modules: frozenset[DJModule]
    distributions: frozenset[DJDistribution]
    module_affiliations: frozenset[DJModuleAffiliation]


class CompRecRepo(ABC):
    """Defines the interface for the repository containing computation records."""

    @abstractmethod
    def add(self, comp_rec: ComputationRecord) -> None:
        """Add the given computation record to the repository if it does not already exist."""

    @abstractmethod
    def remove(self, identifier: Identifier) -> None:
        """Remove the computation record matching the given identifier from the repository if it exists."""

    @abstractmethod
    def get(self, identifier: Identifier) -> ComputationRecord:
        """Get the computation record matching the given identifier from the repository if it exists."""


class DJCompRecRepo(CompRecRepo):
    """Repository that uses DataJoint tables to persist computation records."""

    def __init__(self, translator: DataJointTranslator, rec_table: AbstractTableFacade[DJComputationRecord]) -> None:
        """Initialize the computation record repository."""
        self.translator = translator
        self.rec_table = rec_table

    def add(self, comp_rec: ComputationRecord) -> None:
        """Add the given computation record to the repository if it does not already exist."""
        primary = self.translator.to_primary_key(comp_rec.identifier)

        try:
            self.rec_table[primary] = DJComputationRecord(
                modules=frozenset(self._persist_modules(comp_rec.record.modules)),
                distributions=frozenset(self._persist_dists(comp_rec.record.installed_distributions)),
                module_affiliations=frozenset(self._get_module_affiliations(comp_rec.record.installed_distributions)),
            )
        except ValueError as error:
            raise ValueError(f"Record with identifier '{comp_rec.identifier}' already exists!") from error

    @staticmethod
    def _persist_modules(modules: Iterable[Module]) -> Generator[DJModule, None, None]:
        for module in modules:
            yield DJModule(module_file=str(module.file), module_is_active="True" if module.is_active else "False")

    @staticmethod
    def _persist_dists(dists: Iterable[Distribution]) -> Generator[DJDistribution, None, None]:
        for dist in dists:
            yield DJDistribution(distribution_name=dist.name, distribution_version=dist.version)

    @staticmethod
    def _get_module_affiliations(dists: Iterable[Distribution]) -> Generator[DJModuleAffiliation, None, None]:
        for dist in dists:
            for module in dist.modules:
                yield DJModuleAffiliation(distribution_name=dist.name, module_file=str(module.file))

    def remove(self, identifier: Identifier) -> None:
        """Remove the computation record matching the given identifier from the repository if it exists."""
        primary = self.translator.to_primary_key(identifier)

        try:
            del self.rec_table[primary]
        except KeyError as error:
            raise KeyError(f"Record with identifier '{identifier}' does not exist!") from error

    def get(self, identifier: Identifier) -> ComputationRecord:
        """Get the computation record matching the given identifier from the repository if it exists."""
        primary = self.translator.to_primary_key(identifier)

        try:
            dj_comp_rec = self.rec_table[primary]
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
            self._reconstitue_dist(d, self._filter_dj_modules(d, dj_comp_rec.modules, dj_comp_rec.module_affiliations))
            for d in dj_comp_rec.distributions
        )

    def _filter_dj_modules(
        self, dj_dist: DJDistribution, dj_modules: Iterable[DJModule], dj_affiliations: Iterable[DJModuleAffiliation]
    ) -> Generator[DJModule, None, None]:
        for dj_affiliation in self._filter_dj_affiliations(dj_dist, dj_affiliations):
            try:
                yield next(m for m in dj_modules if m.module_file == dj_affiliation.module_file)
            except StopIteration as error:
                raise ValueError(f"Module referenced in affiliation '{dj_affiliation}' does not exist!") from error

    @staticmethod
    def _filter_dj_affiliations(
        dj_dist: DJDistribution, dj_affiliations: Iterable[DJModuleAffiliation]
    ) -> Generator[DJModuleAffiliation, None, None]:
        return (a for a in dj_affiliations if a.distribution_name == dj_dist.distribution_name)

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

    def __repr__(self) -> str:
        """Return a string representation of the computation record repository."""
        return f"{self.__class__.__name__}(translator={self.translator}, rec_table={self.rec_table})"
