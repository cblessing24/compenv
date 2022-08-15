import textwrap

import pytest

from compenv.model.record import Distribution, InstalledDistributions, Record


class TestRecord:
    @staticmethod
    @pytest.mark.parametrize("attr", ["installed_distributions"])
    def test_attributes_are_read_only(record: Record, attr: str) -> None:
        with pytest.raises(AttributeError):
            setattr(record, attr, "something")

    @staticmethod
    def test_str(record: Record) -> None:
        expected = textwrap.dedent(
            """
            Record:
                Installed Distributions:
                    dist1 (0.1.0)
                    dist2 (0.1.1)
            """
        ).strip()
        assert str(record) == expected


class TestInstalledDistributions:
    @staticmethod
    def test_str(installed_distributions: InstalledDistributions) -> None:
        expected = textwrap.dedent(
            """
            Installed Distributions:
                dist1 (0.1.0)
                dist2 (0.1.1)
            """
        ).strip()
        assert str(installed_distributions) == expected


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
