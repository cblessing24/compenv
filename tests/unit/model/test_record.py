import textwrap

import pytest

from compenv.model.record import ComputationRecord, Distribution


class TestComputationRecord:
    @staticmethod
    @pytest.mark.parametrize("attr", ["distributions"])
    def test_attributes_are_read_only(computation_record: ComputationRecord, attr: str) -> None:
        with pytest.raises(AttributeError):
            setattr(computation_record, attr, "something")

    @staticmethod
    def test_str(computation_record: ComputationRecord) -> None:
        expected = textwrap.dedent(
            """
            Computation Record:
                Distributions:
                    dist1 (0.1.0)
                    dist2 (0.1.1)
            """
        ).strip()
        assert str(computation_record) == expected


class TestDistribution:
    @staticmethod
    def test_str() -> None:
        dist = Distribution("dist", "0.1.0")
        expected = textwrap.dedent(
            """
            Distribution:
                name: dist
                version: 0.1.0
            """
        ).strip()
        assert str(dist) == expected
