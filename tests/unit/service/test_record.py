import pytest

from compenv.model.record import ComputationRecord, Identifier
from compenv.service import record
from compenv.service.abstract import UnitOfWork

from ..conftest import FakeDistributionFinder, FakeOutputPort, FakeRepository, FakeTrigger


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, records: FakeRepository) -> None:
        self.records = records
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        ...


@pytest.fixture
def fake_uow(fake_repository: FakeRepository) -> FakeUnitOfWork:
    return FakeUnitOfWork(fake_repository)


class TestRecord:
    @staticmethod
    @pytest.fixture(autouse=True)
    def record_environment(
        fake_uow: FakeUnitOfWork,
        fake_output_port: FakeOutputPort,
        fake_trigger: FakeTrigger,
        fake_distribution_finder: FakeDistributionFinder,
    ) -> None:
        service = record.RecordService(
            output_port=fake_output_port, uow=fake_uow, distribution_finder=fake_distribution_finder
        )
        request = service.create_request(Identifier("identifier"), fake_trigger)
        service(request)

    @staticmethod
    def test_trigger_is_triggered(fake_trigger: FakeTrigger) -> None:
        assert fake_trigger.triggered

    @staticmethod
    def test_computation_record_is_added_to_repository(
        fake_repository: FakeRepository, computation_record: ComputationRecord
    ) -> None:
        assert fake_repository.get(Identifier("identifier")) == computation_record

    @staticmethod
    def test_unit_of_work_is_committed(fake_uow: FakeUnitOfWork) -> None:
        assert fake_uow.committed

    @staticmethod
    def test_response_is_created(fake_output_port: FakeOutputPort) -> None:
        assert fake_output_port.responses == [record.RecordResponse()]
