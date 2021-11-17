import textwrap
from collections.abc import Set
from pathlib import Path

import pytest

from compenv.model.record import Distribution, Distributions, InstalledDistributions, Module, Modules


class TestRecord:
    @staticmethod
    @pytest.mark.parametrize("attr", ["installed_distributions", "active_distributions", "active_modules"])
    def test_attributes_are_read_only(record, attr):
        with pytest.raises(AttributeError):
            setattr(record, attr, "something")

    @staticmethod
    def test_modules(record):
        assert record.modules == Modules(
            {Module(Path("module1.py"), is_active=False), Module(Path("module2.py"), is_active=True)}
        )

    @staticmethod
    def test_str(record):
        expected = textwrap.dedent(
            """
            Record:
                Installed Distributions:
                    + dist2 (0.1.1)
                    - dist1 (0.1.0)
                Active Modules:
                    module2.py
            """
        ).strip()
        assert str(record) == expected


class TestDistributions:
    @staticmethod
    def test_modules():
        dists = Distributions(
            {
                Distribution(
                    "dist1",
                    "0.1.2",
                    modules=Modules(
                        {Module(Path("module1.py"), is_active=False), Module(Path("module2.py"), is_active=True)}
                    ),
                ),
                Distribution("dist2", "1.2.3", modules=Modules({Module(Path("module3.py"), is_active=False)})),
            }
        )
        assert dists.modules == Modules(
            {
                Module(Path("module1.py"), is_active=False),
                Module(Path("module2.py"), is_active=True),
                Module(Path("module3.py"), is_active=False),
            }
        )


class TestInstalledDistributions:
    @staticmethod
    def test_active_attribute_returns_active_distributions(installed_distributions, active_distributions):
        installed_distributions = InstalledDistributions(installed_distributions)
        assert installed_distributions.active == active_distributions

    @staticmethod
    def test_str(installed_distributions):
        expected = textwrap.dedent(
            """
            Installed Distributions:
                + dist2 (0.1.1)
                - dist1 (0.1.0)
            """
        ).strip()
        assert str(installed_distributions) == expected


class TestActiveDistributions:
    @staticmethod
    def test_str(active_distributions):
        expected = textwrap.dedent(
            """
            Active Distributions:
                + dist2 (0.1.1)
            """
        ).strip()
        assert str(active_distributions) == expected


@pytest.fixture
def modules():
    return Modules(Module(Path("module" + str(i) + ".py"), is_active=False) for i in range(5))


class TestModules:
    @staticmethod
    def test_str(modules):
        expected = textwrap.dedent(
            """
            module0.py
            module1.py
            module2.py
            module3.py
            module4.py
            """
        ).strip()
        assert str(modules) == expected


class TestDistribution:
    @staticmethod
    def test_name_attribute_is_immutable():
        dist = Distribution("dist", "0.1.0")
        with pytest.raises(AttributeError):
            dist.name = "other_dist"

    @staticmethod
    def test_version_attribute_is_immutable():
        dist = Distribution("dist", "0.1.0")
        with pytest.raises(AttributeError):
            dist.version = "0.1.2"

    @staticmethod
    def test_modules_attribute_is_immutable():
        dist = Distribution("dist", "0.1.0")
        with pytest.raises(AttributeError):
            dist.modules = {}

    @staticmethod
    def test_module_in_distribution_if_module_in_modules():
        module = Module(Path("module.py"), is_active=False)
        dist = Distribution("dist", "0.1.0", modules=frozenset((module,)))
        assert (module in dist) is True

    @staticmethod
    def test_module_not_in_distribution_if_module_not_in_modules():
        module = Module(Path("module.py"), is_active=False)
        dist = Distribution("dist", "0.1.0")
        assert (module in dist) is False

    @staticmethod
    def test_iterating_distribution_iterates_modules(modules):
        dist = Distribution("dist", "0.1.0", modules=modules)
        assert frozenset(dist) == modules

    @staticmethod
    def test_length_of_distribution_is_equal_to_length_of_modules(modules):
        dist = Distribution("dist", "0.1.0", modules=modules)
        assert len(dist) == len(modules)

    @staticmethod
    def test_distribution_is_instance_of_set_class():
        dist = Distribution("dist", "0.1.0")
        assert isinstance(dist, Set)

    @staticmethod
    @pytest.mark.parametrize("is_actives,expected", [([False, False, False], False), ([False, True, False], True)])
    def test_distributions_is_active_property(is_actives, expected):
        modules = frozenset(Module(Path("module" + str(i) + ".py"), is_active=ia) for i, ia in enumerate(is_actives))
        dist = Distribution("dist", "0.1.0", modules=modules)
        assert dist.is_active is expected

    @staticmethod
    def test_str(modules):
        dist = Distribution("dist", "0.1.0", modules=modules)
        expected = textwrap.dedent(
            """
            Distribution:
                name: dist
                version: 0.1.0
                modules:
                    module0.py
                    module1.py
                    module2.py
                    module3.py
                    module4.py
            """
        ).strip()
        assert str(dist) == expected

    @staticmethod
    @pytest.mark.parametrize("method", ["__and__", "__or__", "__sub__", "__xor__"])
    def test_set_methods_produce_expected_result(method):
        modules1 = frozenset(Module(Path("module" + str(i) + ".py"), is_active=False) for i in [1, 2, 3])
        modules2 = frozenset(Module(Path("module" + str(i) + ".py"), is_active=False) for i in [4, 5, 6])
        dist1 = Distribution("dist1", "0.1.0", modules=modules1)
        dist2 = Distribution("dist2", "0.1.0", modules=modules2)
        assert getattr(dist1, method)(dist2) == getattr(modules1, method)(modules2)


class TestActiveModules:
    @staticmethod
    def test_str(active_modules):
        expected = textwrap.dedent(
            """
            Active Modules:
                module2.py
            """
        ).strip()
        assert str(active_modules) == expected


class TestModule:
    @staticmethod
    def test_file_attribute_is_immutable():
        module = Module(Path("module.py"), is_active=False)
        with pytest.raises(AttributeError):
            module.file = Path("other_file.py")

    @staticmethod
    def test_module_is_not_equal_to_non_module_object():
        module = Module(Path("module.py"), is_active=False)
        other = object()
        assert (module == other) is False

    @staticmethod
    def test_modules_are_equal_if_their_files_are_equal():
        module1, module2 = (Module(Path("module.py"), is_active=False) for _ in range(2))
        assert (module1 == module2) is True

    @staticmethod
    def test_modules_are_not_equal_if_their_files_are_not_equal():
        module1 = Module(Path("module.py"), is_active=False)
        module2 = Module(Path("other_module.py"), is_active=False)
        assert (module1 == module2) is False

    @staticmethod
    def test_modules_have_same_hash_if_their_files_are_equal():
        module1, module2 = (Module(Path("module.py"), is_active=False) for _ in range(2))
        assert (hash(module1) == hash(module2)) is True

    @staticmethod
    def test_modules_have_different_hashes_if_their_files_are_not_equal():
        module1 = Module(Path("module.py"), is_active=False)
        module2 = Module(Path("other_module.py"), is_active=False)
        assert (hash(module1) == hash(module2)) is False

    @staticmethod
    def test_repr():
        file = Path("module.py")
        module = Module(file, is_active=False)
        assert repr(module) == f"Module(file={repr(file)}, is_active=False)"
