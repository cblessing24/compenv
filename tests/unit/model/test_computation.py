import textwrap

import pytest

from compenv.model.computation import Temp


class TestComputationRecord:
    @staticmethod
    @pytest.mark.parametrize("attr", ["identifier", "record"])
    def test_attributes_are_immutable(computation_record: Temp, attr: str) -> None:
        with pytest.raises(AttributeError):
            setattr(computation_record, attr, "another_value")

    @staticmethod
    def test_str(computation_record: Temp) -> None:
        expected = textwrap.dedent(
            """
            Computation Record:
                Identifier: identifier
                Record:
                    Distributions:
                        dist1 (0.1.0)
                        dist2 (0.1.1)
            """
        ).strip()
        assert str(computation_record) == expected
