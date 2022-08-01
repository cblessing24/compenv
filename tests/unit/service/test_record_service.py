import pytest

from compenv.model.computation import ComputationRecord, Identifier
from compenv.service import record

from ..conftest import FakeRepository, FakeTrigger
from .conftest import FakeOutputPort


@pytest.mark.usefixtures("prepare_environment")
class TestRecord:
    @staticmethod
    @pytest.fixture(autouse=True)
    def record_environment(
        fake_repository: FakeRepository, fake_output_port: FakeOutputPort, fake_trigger: FakeTrigger
    ) -> None:
        service = record.RecordService(fake_repository, output_port=fake_output_port)
        request = service.create_request(Identifier("identifier"), fake_trigger)
        service(request)

    @staticmethod
    def test_trigger_is_triggered(fake_trigger: FakeTrigger) -> None:
        assert fake_trigger.triggered

    @staticmethod
    def test_computation_record_is_added_to_repository(
        fake_repository: FakeRepository, computation_record: ComputationRecord
    ) -> None:
        assert fake_repository.get("identifier") == computation_record  # type: ignore[no-untyped-call]

    @staticmethod
    def test_response_is_created(fake_output_port: FakeOutputPort) -> None:
        assert fake_output_port.responses == [record.RecordResponse()]
