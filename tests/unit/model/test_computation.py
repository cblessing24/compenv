import textwrap
from typing import Any, List

import pytest

from compenv.model.computation import Computation, ComputationRecord, Identifier
from compenv.model.environment import Environment
from compenv.model.record import Record

from ..conftest import FakeTrigger


@pytest.mark.usefixtures("prepare_environment")
class TestComputation:
    @staticmethod
    @pytest.fixture
    def recorded_records() -> List[Record]:
        return []

    @staticmethod
    @pytest.fixture
    def environment(recorded_records: List[Record]) -> Environment:
        original_record = Environment.record

        def tracking_record(*args: Any, **kwargs: Any) -> Record:
            record = original_record(*args, **kwargs)
            recorded_records.append(record)
            return record

        Environment.record = staticmethod(tracking_record)  # type: ignore[assignment]
        return Environment()

    @staticmethod
    @pytest.fixture
    def computation(environment: Environment, fake_trigger: FakeTrigger) -> Computation:
        return Computation(Identifier("identifier"), environment, trigger=fake_trigger)

    @staticmethod
    def test_computation_record_gets_returned_when_computation_gets_executed(
        computation: Computation, record: Record
    ) -> None:
        assert computation.execute() == ComputationRecord(Identifier("identifier"), record)

    @staticmethod
    def test_computation_record_is_based_on_record_recorded_after_execution(
        computation: Computation, recorded_records: List[Record]
    ) -> None:
        assert computation.execute().record is recorded_records[1]

    @staticmethod
    def test_trigger_gets_triggered_when_computation_gets_executed(
        computation: Computation, fake_trigger: FakeTrigger
    ) -> None:
        computation.execute()
        assert fake_trigger.triggered

    @staticmethod
    def test_computation_can_not_be_executed_more_than_once(computation: Computation) -> None:
        computation.execute()
        with pytest.raises(RuntimeError, match="Computation already executed!"):
            computation.execute()

    @staticmethod
    def test_computation_raises_warning_if_environment_changes_during_computation(
        computation: Computation, fake_trigger: FakeTrigger
    ) -> None:
        fake_trigger.change_environment = True
        with pytest.warns(UserWarning, match="Environment changed during execution!"):
            computation.execute()

    @staticmethod
    def test_computation_raises_no_warning_if_environment_does_not_change_during_computation(
        computation: Computation,
    ) -> None:
        with pytest.warns(None) as record:
            computation.execute()
            assert not record

    @staticmethod
    def test_repr(computation: Computation) -> None:
        assert (
            repr(computation)
            == f"Computation(identifier='identifier', environment=Environment(), trigger=FakeTrigger())"
        )


class TestComputationRecord:
    @staticmethod
    @pytest.mark.parametrize("attr", ["identifier", "record"])
    def test_attributes_are_immutable(computation_record: ComputationRecord, attr: str) -> None:
        with pytest.raises(AttributeError):
            setattr(computation_record, attr, "another_value")

    @staticmethod
    def test_str(computation_record: ComputationRecord) -> None:
        expected = textwrap.dedent(
            """
            Computation Record:
                Identifier: identifier
                Record:
                    Installed Distributions:
                        dist1 (0.1.0)
                        dist2 (0.1.1)
            """
        ).strip()
        assert str(computation_record) == expected
