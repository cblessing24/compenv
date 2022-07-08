import pytest

from compenv.service import record


@pytest.mark.usefixtures("prepare_environment")
class TestRecord:
    @staticmethod
    @pytest.fixture(autouse=True)
    def record_environment(fake_repository, fake_output_port, fake_trigger):
        service = record.RecordService(fake_repository, output_port=fake_output_port)
        request = service.create_request("identifier", fake_trigger)
        service(request)

    @staticmethod
    def test_trigger_is_triggered(fake_trigger):
        assert fake_trigger.triggered

    @staticmethod
    def test_computation_record_is_added_to_repository(fake_repository, computation_record):
        assert fake_repository["identifier"] == computation_record

    @staticmethod
    def test_response_is_created(fake_output_port):
        assert fake_output_port.responses == [record.RecordResponse()]
