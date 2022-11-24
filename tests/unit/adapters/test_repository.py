from __future__ import annotations

from typing import Iterable, Optional, Protocol

import pytest

from compenv.adapters.entity import DJComputationRecord
from compenv.adapters.repository import ComputationRegistryTracker, DJRepository
from compenv.model.computation import Computation, ComputationRegistry
from compenv.model.record import ComputationRecord, Identifier
from compenv.types import PrimaryKey

from ...conftest import ComputationCreator, RegistryCreator
from ..conftest import FakeTranslatorFactory
from .conftest import FakeRecordTableFacade


@pytest.fixture
def repo(fake_translator_factory: FakeTranslatorFactory, fake_table: FakeRecordTableFacade) -> DJRepository:
    return DJRepository(fake_translator_factory(), fake_table)


@pytest.fixture
def add_computation_record(repo: DJRepository, computation_record: ComputationRecord) -> None:
    repo.add(computation_record)


@pytest.mark.usefixtures("add_computation_record")
class TestAdd:
    @staticmethod
    def test_raises_error_if_already_existing(repo: DJRepository, computation_record: ComputationRecord) -> None:
        with pytest.raises(ValueError, match="already exists!"):
            repo.add(computation_record)

    @staticmethod
    def test_inserts_dj_computation_record(
        fake_table: FakeRecordTableFacade, primary: PrimaryKey, dj_comp_rec: DJComputationRecord
    ) -> None:
        assert fake_table.get(primary) == dj_comp_rec


def test_raises_error_if_not_existing(repo: DJRepository, identifier: Identifier) -> None:
    with pytest.raises(KeyError, match="does not exist!"):
        _ = repo.get(identifier)


class TestGet:
    @staticmethod
    @pytest.mark.usefixtures("add_computation_record")
    def test_gets_computation_record_if_existing(
        repo: DJRepository, computation_record: ComputationRecord, identifier: Identifier
    ) -> None:
        assert repo.get(identifier) == computation_record


def test_iteration(repo: DJRepository, computation_record: ComputationRecord) -> None:
    repo.add(computation_record)
    assert list(iter(repo)) == [computation_record.identifier]


def test_length(repo: DJRepository, computation_record: ComputationRecord) -> None:
    repo.add(computation_record)
    assert len(repo) == 1


def test_repr(repo: DJRepository) -> None:
    assert repr(repo) == "DJRepository(translator=FakeTranslator(), table=FakeRecordTableFacade())"


class TestComputationRegistryTracker:
    class TrackedRegistryCreator(Protocol):
        def __call__(
            self, algorithm_name: str, computations: Optional[Iterable[Computation]] = ...
        ) -> tuple[ComputationRegistryTracker, ComputationRegistry]:
            ...

    @staticmethod
    @pytest.fixture
    def create_tracked_registry(create_registry: RegistryCreator) -> TrackedRegistryCreator:
        def create(
            algorithm_name: str, computations: Optional[Iterable[Computation]] = None
        ) -> tuple[ComputationRegistryTracker, ComputationRegistry]:
            tracker = ComputationRegistryTracker()
            registry = create_registry(algorithm_name, computations)
            tracker.track(registry)
            return tracker, registry

        return create

    @staticmethod
    def test_can_track_registry(
        create_tracked_registry: TrackedRegistryCreator,
        create_computation: ComputationCreator,
    ) -> None:
        tracker, registry = create_tracked_registry("myalgorithm")
        computation = create_computation("myalgorithm", "myarguments")
        registry.add(computation)
        assert set(tracker.changes) == {computation}

    @staticmethod
    def test_tracking_same_registry_twice_does_nothing(
        create_tracked_registry: TrackedRegistryCreator, create_computation: ComputationCreator
    ) -> None:
        tracker, registry = create_tracked_registry("myalgorithm")
        computation = create_computation("myalgorithm", "myarguments")
        registry.add(computation)
        tracker.track(registry)
        assert set(tracker.changes) == {computation}

    @staticmethod
    def test_can_clear_tracker(
        create_tracked_registry: TrackedRegistryCreator, create_computation: ComputationCreator
    ) -> None:
        tracker, registry = create_tracked_registry("myalgorithm")
        computation = create_computation("myalgorithm", "myarguments")
        registry.add(computation)
        tracker.clear()
        assert set(tracker.changes) == set()
