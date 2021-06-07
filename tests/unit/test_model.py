import pytest

from repro.model import Distribution, ModularUnit, Module, Package


class TestModularUnit:
    @staticmethod
    @pytest.mark.parametrize("attr", ["name", "file"])
    def test_attributes_are_read_only(attr):
        with pytest.raises(AttributeError):
            setattr(ModularUnit("module"), attr, "something")

    @staticmethod
    @pytest.mark.parametrize("func", ["__eq__", "__contains__"])
    def test_equality_and_contains_checks_return_false_when_called_with_non_modular_unit_object(func):
        assert getattr(ModularUnit("module"), func)(object()) is False

    @staticmethod
    @pytest.fixture(
        params=[
            ([("module", "file"), ("module", "file")], True),
            ([("module", "file"), ("other_module", "file")], False),
            ([("module", "file"), ("module", "other_file")], False),
            ([("module", "file"), ("other_module", "other_file")], False),
        ]
    )
    def test_case(request):
        units_data, expected = request.param
        units = tuple(ModularUnit(n, file=f) for (n, f) in units_data)
        return units, expected

    @staticmethod
    @pytest.mark.parametrize("func", ["__eq__", "__contains__"])
    def test_equality_and_contains_checks_produces_expected_result(test_case, func):
        (unit1, unit2), expected = test_case
        assert getattr(unit1, func)(unit2) is expected

    @staticmethod
    def test_hash_produces_expected_result(test_case):
        (unit1, unit2), expected = test_case
        assert (hash(unit1) == hash(unit2)) is expected

    @staticmethod
    def test_repr():
        module = ModularUnit("module")
        assert repr(module) == "ModularUnit(name='module', file=None)"


class TestPackage:
    @staticmethod
    def test_modular_unit_in_package_if_in_package_itself():
        unit = ModularUnit("module")
        package = Package("package", units=[unit])
        assert unit in package

    @staticmethod
    def test_modular_unit_in_package_if_in_sub_package():
        unit = ModularUnit("module")
        sub_package = Package("sub-package", units=[unit])
        package = Package("package", units=[sub_package])
        assert unit in package

    @staticmethod
    def test_module_not_in_package_if_not_in_package_or_sub_packages():
        module = Module("module")
        package = Package("package")
        assert module not in package

    @staticmethod
    def test_equality_check_returns_false_when_called_with_non_modular_unit_object():
        assert (Package("package") == object()) is False

    @staticmethod
    @pytest.fixture(
        params=[
            ([("package", "file", {"module"}), ("package", "file", {"module"})], True),
            ([("package", "file", {"module"}), ("other_package", "file", {"module"})], False),
            ([("package", "file", {"module"}), ("package", "other_file", {"module"})], False),
            ([("package", "file", {"module"}), ("package", "file", {"other_module"})], False),
        ]
    )
    def test_case(request):
        package_data, expected = request.param
        packages = tuple(Package(n, file=f, units=(Module(u) for u in us)) for (n, f, us) in package_data)
        return packages, expected

    @staticmethod
    def test_equality_check_produces_expected_result(test_case):
        (package1, package2), expected = test_case
        assert (package1 == package2) is expected

    @staticmethod
    def test_hash_produces_expected_result(test_case):
        (package1, package2), expected = test_case
        assert (hash(package1) == hash(package2)) is expected


class TestDistribution:
    @staticmethod
    @pytest.fixture
    def package():
        return Package("package")

    @staticmethod
    @pytest.fixture
    def distribution(package):
        return Distribution("dist", "0.1.2", packages=[package])

    @staticmethod
    @pytest.mark.parametrize("attr", ["name", "version"])
    def test_attributes_are_read_only(distribution, attr):
        with pytest.raises(AttributeError):
            setattr(distribution, attr, "something")

    @staticmethod
    def test_contains_returns_false_when_called_with_non_modular_unit_object(distribution):
        assert (object() in distribution) is False

    @staticmethod
    def test_modular_unit_in_distribution_if_in_any_package(distribution, package):
        assert package in distribution

    @staticmethod
    def test_modular_unit_not_in_distribution_if_not_in_any_package(distribution):
        assert Package("other-package") not in distribution

    @staticmethod
    def test_equality_check_returns_false_when_called_with_non_modular_unit_object(distribution):
        assert (distribution == object()) is False

    @staticmethod
    @pytest.fixture(
        params=[
            ([("dist", "version", {"package"}), ("dist", "version", {"package"})], True),
            ([("dist", "version", {"package"}), ("other_dist", "version", {"package"})], False),
            ([("dist", "version", {"package"}), ("dist", "other_version", {"package"})], False),
            ([("dist", "version", {"package"}), ("dist", "version", {"other_package"})], False),
        ]
    )
    def test_case(request):
        dist_data, expected = request.param
        dists = tuple(Distribution(n, version=v, packages=(Package(p) for p in ps)) for (n, v, ps) in dist_data)
        return dists, expected

    @staticmethod
    def test_equality_check_produces_expected_result(test_case):
        (dist1, dist2), expected = test_case
        assert (dist1 == dist2) is expected

    @staticmethod
    def test_hash_produces_expected_result(test_case):
        (dist1, dist2), expected = test_case
        assert (hash(dist1) == hash(dist2)) is expected

    @staticmethod
    def test_repr(distribution):
        assert repr(distribution) == "Distribution(name='dist', version='0.1.2')"
