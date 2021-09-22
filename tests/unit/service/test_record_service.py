import pytest

from repro.service import record
from repro.service.abstract import ComputationRecordRepository


@pytest.fixture
def fake_repository():
    class FakeRespository(dict, ComputationRecordRepository):
        pass

    return FakeRespository()


@pytest.mark.usefixtures("prepare_environment")
class TestRecord:
    @staticmethod
    @pytest.fixture(autouse=True)
    def record_environment(fake_repository, fake_trigger):
        service = record.RecordService(fake_repository)
        request = service.create_request("identifier", fake_trigger)
        service(request)

    @staticmethod
    def test_trigger_is_triggered(fake_trigger):
        assert fake_trigger.triggered

    @staticmethod
    def test_computation_record_is_added_to_repository(fake_repository, computation_record):
        assert fake_repository["identifier"] == computation_record
