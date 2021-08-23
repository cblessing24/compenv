import pytest

from repro.service import record
from repro.service.abstract import ComputationRecordRepository


@pytest.fixture
def fake_repository():
    class FakeRespository(dict, ComputationRecordRepository):
        pass

    return FakeRespository()


def test_trigger_is_triggered(environment, fake_repository, fake_trigger):
    record.record(fake_repository, "identifier", fake_trigger)
    assert fake_trigger.triggered


def test_computation_record_is_added_to_repository(environment, fake_repository, fake_trigger, computation_record):
    record.record(fake_repository, "identifier", fake_trigger)
    assert fake_repository["identifier"] == computation_record
