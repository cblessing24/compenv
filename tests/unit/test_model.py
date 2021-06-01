import pytest

from repro.model import Distribution, ModularUnit, Module, Package


class TestModularUnit:
    @staticmethod
    def test_contains_raises_error_when_called_with_non_modular_unit_object():
        with pytest.raises(TypeError):
            object() in ModularUnit("module", file=None)

    @staticmethod
    def test_modular_unit_contains_itself():
        module = ModularUnit("module", file=None)
        assert module in module


class TestPackage:
    @staticmethod
    def test_modular_unit_in_package_if_in_package_itself():
        unit = ModularUnit("module", file=None)
        package = Package("package", file=None, units={unit})
        assert unit in package

    @staticmethod
    def test_modular_unit_in_package_if_in_sub_package():
        unit = ModularUnit("module", file=None)
        sub_package = Package("sub-package", file=None, units=frozenset([unit]))
        package = Package("package", file=None, units=frozenset([sub_package]))
        assert unit in package

    @staticmethod
    def test_module_not_in_package_if_not_in_package_or_sub_packages():
        module = Module("module", file=None)
        package = Package("package", file=None, units=frozenset())
        assert module not in package


class TestDistribution:
    @staticmethod
    @pytest.fixture
    def package():
        return Package("package", file=None, units=frozenset())

    @staticmethod
    @pytest.fixture
    def distribution(package):
        return Distribution("dist", "0.1.2", packages=frozenset([package]))

    @staticmethod
    def test_contains_raises_error_when_called_with_non_modular_unit_object(distribution):
        with pytest.raises(TypeError):
            object() in distribution

    @staticmethod
    def test_modular_unit_in_distribution_if_in_any_package(distribution, package):
        assert package in distribution

    @staticmethod
    def test_modular_unit_not_in_distribution_if_not_in_any_package(distribution):
        assert Package("other-package", file=None, units=frozenset()) not in distribution
