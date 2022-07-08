import textwrap

import pytest

from compenv.model.computation import Computation, ComputationRecord
from compenv.model.environment import Environment


@pytest.mark.usefixtures("prepare_environment")
class TestComputation:
    @staticmethod
    @pytest.fixture
    def recorded_records():
        return []

    @staticmethod
    @pytest.fixture
    def environment(recorded_records):
        original_record = Environment.record

        def tracking_record(*args, **kwargs):
            record = original_record(*args, **kwargs)
            recorded_records.append(record)
            return record

        Environment.record = staticmethod(tracking_record)
        return Environment()

    @staticmethod
    @pytest.fixture
    def computation(environment, fake_trigger):
        return Computation("identifier", environment, trigger=fake_trigger)

    @staticmethod
    def test_computation_record_gets_returned_when_computation_gets_executed(computation, record):
        assert computation.execute() == ComputationRecord("identifier", record)

    @staticmethod
    def test_computation_record_is_based_on_record_recorded_after_execution(computation, recorded_records):
        assert computation.execute().record is recorded_records[1]

    @staticmethod
    def test_trigger_gets_triggered_when_computation_gets_executed(computation, fake_trigger):
        computation.execute()
        assert fake_trigger.triggered

    @staticmethod
    def test_computation_can_not_be_executed_more_than_once(computation):
        computation.execute()
        with pytest.raises(RuntimeError, match="Computation already executed!"):
            computation.execute()

    @staticmethod
    def test_computation_raises_warning_if_environment_changes_during_computation(computation, fake_trigger):
        fake_trigger.change_environment = True
        with pytest.warns(UserWarning, match="Environment changed during execution!"):
            computation.execute()

    @staticmethod
    def test_computation_raises_no_warning_if_environment_does_not_change_during_computation(computation):
        with pytest.warns(None) as record:
            computation.execute()
            assert not record

    @staticmethod
    def test_repr(computation):
        assert (
            repr(computation)
            == f"Computation(identifier='identifier', environment=Environment(), trigger=FakeTrigger())"
        )


class TestComputationRecord:
    @staticmethod
    @pytest.mark.parametrize("attr", ["identifier", "record"])
    def test_attributes_are_immutable(computation_record, attr):
        with pytest.raises(AttributeError):
            setattr(computation_record, attr, "another_value")

    @staticmethod
    def test_str(computation_record):
        expected = textwrap.dedent(
            """
            Computation Record:
                Identifier: identifier
                Record:
                    Installed Distributions:
                        + dist2 (0.1.1)
                        - dist1 (0.1.0)
                    Active Modules:
                        module2.py
            """
        ).strip()
        assert str(computation_record) == expected
