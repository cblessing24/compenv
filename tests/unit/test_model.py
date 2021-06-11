from collections.abc import Set
from pathlib import Path

import pytest

from repro.model import Distribution, Module


class TestModule:
    @staticmethod
    def test_file_attribute_is_immutable():
        module = Module(Path("module.py"))
        with pytest.raises(AttributeError):
            module.file = Path("other_file.py")

    @staticmethod
    def test_module_is_not_equal_to_non_module_object():
        module = Module(Path("module.py"))
        other = object()
        assert (module == other) is False

    @staticmethod
    def test_modules_are_equal_if_their_files_are_equal():
        module1, module2 = (Module(Path("module.py")) for _ in range(2))
        assert (module1 == module2) is True

    @staticmethod
    def test_modules_are_not_equal_if_their_files_are_not_equal():
        module1 = Module(Path("module.py"))
        module2 = Module(Path("other_module.py"))
        assert (module1 == module2) is False

    @staticmethod
    def test_modules_have_same_hash_if_their_files_are_equal():
        module1, module2 = (Module(Path("module.py")) for _ in range(2))
        assert (hash(module1) == hash(module2)) is True

    @staticmethod
    def test_modules_have_different_hashes_if_their_files_are_not_equal():
        module1 = Module(Path("module.py"))
        module2 = Module(Path("other_module.py"))
        assert (hash(module1) == hash(module2)) is False

    @staticmethod
    def test_repr():
        file = Path("module.py")
        module = Module(file)
        assert repr(module) == f"Module(file={repr(file)})"


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
        module = Module("module.py")
        dist = Distribution("dist", "0.1.0", modules=frozenset((module,)))
        assert (module in dist) is True

    @staticmethod
    def test_module_not_in_distribution_if_module_not_in_modules():
        module = Module("module.py")
        dist = Distribution("dist", "0.1.0")
        assert (module in dist) is False

    @staticmethod
    def test_iterating_distribution_iterates_modules():
        modules = frozenset(Module("module" + str(i) + ".py") for i in range(5))
        dist = Distribution("dist", "0.1.0", modules=modules)
        assert frozenset(dist) == modules

    @staticmethod
    def test_length_of_distribution_is_equal_to_length_of_modules():
        modules = frozenset(Module("module" + str(i) + ".py") for i in range(5))
        dist = Distribution("dist", "0.1.0", modules=modules)
        assert len(dist) == len(modules)

    @staticmethod
    def test_distribution_is_instance_of_set_class():
        dist = Distribution("dist", "0.1.0")
        assert isinstance(dist, Set)

    @staticmethod
    @pytest.mark.parametrize("method", ["__and__", "__or__", "__sub__", "__xor__"])
    def test_set_methods_produce_expected_result(method):
        modules1 = frozenset(Module("module" + str(i) + ".py") for i in [1, 2, 3])
        modules2 = frozenset(Module("module" + str(i) + ".py") for i in [4, 5, 6])
        dist1 = Distribution("dist1", "0.1.0", modules=modules1)
        dist2 = Distribution("dist2", "0.1.0", modules=modules2)
        assert getattr(dist1, method)(dist2) == getattr(modules1, method)(modules2)
