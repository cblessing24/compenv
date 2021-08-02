import pytest

from repro.model import record
from repro.model.model import Computation, ComputationRecord, Environment


class TestComputationRecord:
    @staticmethod
    @pytest.fixture
    def computation_record(record):
        return ComputationRecord("identifier", record)

    @staticmethod
    @pytest.mark.parametrize("attr", ["identifier", "record"])
    def test_attributes_are_immutable(computation_record, attr):
        with pytest.raises(AttributeError):
            setattr(computation_record, attr, "another_value")


@pytest.fixture
def environment(installed_distributions, active_modules):
    def fake_get_active_modules():
        return iter(active_modules)

    def fake_get_installed_distributions():
        return iter(installed_distributions)

    record.get_active_modules = fake_get_active_modules
    record.get_installed_distributions = fake_get_installed_distributions
    return Environment()


class TestComputation:
    @staticmethod
    @pytest.fixture
    def recorded_records():
        return []

    @staticmethod
    @pytest.fixture
    def environment(environment, recorded_records):
        original_record = Environment.record

        def tracking_record(*args, **kwargs):
            record = original_record(*args, **kwargs)
            recorded_records.append(record)
            return record

        Environment.record = staticmethod(tracking_record)
        return Environment()

    @staticmethod
    @pytest.fixture
    def fake_trigger():
        class FakeTrigger:
            triggered = False
            change_environment = False

            def __call__(self):
                if self.change_environment:
                    self._change_environment()
                self.triggered = True

            def _change_environment(self):
                def fake_get_active_modules():
                    return iter(frozenset())

                record.get_active_modules = fake_get_active_modules

            def __repr__(self):
                return f"{self.__class__.__name__}()"

        return FakeTrigger()

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


class TestEnvironment:
    @staticmethod
    def test_correct_record_is_recorded(environment, record):
        assert environment.record() == record

    @staticmethod
    @pytest.mark.parametrize("attr", ["success", "record"])
    def test_consistency_check_attributes_can_not_be_accessed_in_with_block(environment, attr):
        with pytest.raises(RuntimeError, match=f"Can not access '{attr}'"):
            with environment.consistency_check() as check:
                getattr(check, attr)

    @staticmethod
    def test_consistency_check_repr(environment):
        with environment.consistency_check() as check:
            assert repr(check) == "_ConsistencyCheck(environment=Environment())"

    @staticmethod
    def test_repr(environment):
        assert repr(environment) == "Environment()"
