import pytest

from repro.model import Distribution, ModularUnit, Module, Package


class TestModularUnit:
    @staticmethod
    def test_contains_raises_error_when_called_with_non_modular_unit_object():
        with pytest.raises(TypeError):
            object in ModularUnit("module", file=None)

    @staticmethod
    def test_modular_unit_contains_itself():
        module = ModularUnit("module", file=False)
        assert module in module


class TestPackage:
    @staticmethod
    def test_modular_unit_in_package_if_in_package_itself():
        unit = ModularUnit("module", file=None)
        package = Package("package", file=None, units={unit})
        assert unit in package

    @staticmethod
    def test_modular_unit_in_package_if_in_sub_package():
        modular_unit = ModularUnit("module", file=None)
        sub_package = Package("sub-package", file=None, units=frozenset([modular_unit]))
        package = Package("package", file=None, units=frozenset([sub_package]))
        assert modular_unit in package

    @staticmethod
    def test_module_not_in_package_if_not_in_package_or_sub_packages():
        module = Module("module", file=None)
        package = Package("package", file=None, units=frozenset())
        assert module not in package


class TestDistribution:
    @staticmethod
    @pytest.fixture
    def distribution():
        return Distribution("bar", "0.1.0", {Module("module", "/foo/module.py")})

    @staticmethod
    def test_non_module_object_not_in_distribution(distribution):
        assert object() not in distribution

    @staticmethod
    def test_module_in_distribution_if_module_in_distribution_modules(distribution):
        module = Module("module", "/foo/module.py")
        assert module in distribution

    @staticmethod
    def test_module_not_in_distribution_if_module_not_in_distribution_modules(distribution):
        module = Module("foo", "/bar/module.py")
        assert module not in distribution

    @staticmethod
    def test_length_equal_to_number_of_modules_in_distribution(distribution):
        assert len(distribution) == 1

    @staticmethod
    def test_iterating_distribution_iterates_modules(distribution):
        assert next(iter(distribution)) == Module("module", "/foo/module.py")
