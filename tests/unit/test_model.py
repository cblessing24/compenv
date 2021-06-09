import pytest

from repro.model import Distribution, ModularUnit, Module, Package


class TestModularUnit:
    @staticmethod
    def test_file_attribute_is_read_only():
        with pytest.raises(AttributeError):
            ModularUnit("file").file = "other_file"

    @staticmethod
    @pytest.mark.parametrize("func", ["__eq__", "__contains__"])
    def test_equality_and_contains_checks_return_false_when_called_with_non_modular_unit_object(func):
        assert getattr(ModularUnit("file"), func)(object()) is False

    @staticmethod
    @pytest.fixture(
        params=[
            (["file", "file"], True),
            (["file", "other_file"], False),
        ]
    )
    def test_case(request):
        units_files, expected = request.param
        units = tuple(ModularUnit(f) for f in units_files)
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
        module = ModularUnit("file")
        assert repr(module) == "ModularUnit(file='file')"


class TestPackage:
    @staticmethod
    def test_modular_unit_in_package_if_in_package_itself():
        unit = ModularUnit("unit_file")
        package = Package("package_file", units=[unit])
        assert unit in package

    @staticmethod
    def test_modular_unit_in_package_if_in_sub_package():
        unit = ModularUnit("unit_file")
        sub_package = Package("sub_package_file", units=[unit])
        package = Package("package_file", units=[sub_package])
        assert unit in package

    @staticmethod
    def test_module_not_in_package_if_not_in_package_or_sub_packages():
        module = Module("module_file")
        package = Package("package_file")
        assert module not in package

    @staticmethod
    def test_equality_check_returns_false_when_called_with_non_modular_unit_object():
        assert (Package("package_file") == object()) is False

    @staticmethod
    @pytest.fixture(
        params=[
            ([("package_file", {"module"}), ("package_file", {"module"})], True),
            ([("package_file", {"module"}), ("other_package_file", {"module"})], False),
            ([("package_file", {"module"}), ("package_file", {"other_module"})], False),
            ([("package_file", {"module"}), ("other_package_file", {"other_module"})], False),
        ]
    )
    def test_case(request):
        package_files, expected = request.param
        packages = tuple(Package(pf, units=(Module(mf) for mf in mfs)) for (pf, mfs) in package_files)
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
        return Package("package_file")

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
        assert Package("other_package_file") not in distribution

    @staticmethod
    def test_equality_check_returns_false_when_called_with_non_modular_unit_object(distribution):
        assert (distribution == object()) is False

    @staticmethod
    @pytest.fixture(
        params=[
            ([("dist", "version", {"package_file"}), ("dist", "version", {"package_file"})], True),
            ([("dist", "version", {"package_file"}), ("other_dist", "version", {"package_file"})], False),
            ([("dist", "version", {"package_file"}), ("dist", "other_version", {"package_file"})], False),
            ([("dist", "version", {"package_file"}), ("dist", "version", {"other_package_file"})], False),
        ]
    )
    def test_case(request):
        dist_data, expected = request.param
        dists = tuple(Distribution(n, version=v, packages=(Package(pf) for pf in pfs)) for (n, v, pfs) in dist_data)
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
