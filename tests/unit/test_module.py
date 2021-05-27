import os
import sys

import pytest

from repro.model import Module
from repro.module import LoadedModuleConverter, is_built_in_module, is_bundled_module, is_stdlib_module


class FakeModule:
    def __init__(self, spec=None):
        self.__spec__ = spec


class Spec:
    def __init__(self, origin):
        self.origin = origin


@pytest.fixture
def built_in_module():
    spec = Spec("built-in")
    module = FakeModule(spec)
    return module


@pytest.fixture
def bundled_module():
    module = FakeModule()
    module.__file__ = os.path.join(
        sys.prefix, sys.platlibdir, f"python{sys.version_info.major}.{sys.version_info.minor}", "module"
    )
    return module


class TestIsBuiltInModule:
    def test_if_false_is_returned_if_module_spec_is_none(self):
        assert is_built_in_module(FakeModule()) is False

    def test_if_true_is_returned_if_origin_of_module_spec_is_built_in(self, built_in_module):
        assert is_built_in_module(built_in_module) is True

    def test_if_false_is_returned_if_origin_of_module_spec_is_not_built_in(self):
        spec = Spec("not-built-in")
        module = FakeModule(spec)
        assert is_built_in_module(module) is False


class TestIsBundledModule:
    def test_if_false_is_returned_if_module_has_no_file(self):
        assert is_bundled_module(FakeModule()) is False

    def test_if_true_is_returned_if_module_in_stdlib_dir(self, bundled_module):
        assert is_bundled_module(bundled_module) is True

    def test_if_false_is_returned_if_module_not_in_stdlib_dir(self):
        module = FakeModule()
        module.__file__ = "/not/stdlib/module.py"
        assert is_bundled_module(module) is False


class TestIsStdlibModule:
    def test_if_true_is_returned_if_module_is_built_in(self, built_in_module):
        assert is_stdlib_module(built_in_module) is True

    def test_if_true_is_returned_if_module_is_bundled(self, bundled_module):
        assert is_stdlib_module(bundled_module) is True

    def test_if_false_is_returned_if_module_is_not_built_in_nor_bundled(self):
        assert is_stdlib_module(FakeModule()) is False


class TestLoadedModuleConverter:
    @pytest.fixture
    def fake_loaded_modules(self):
        class FakeModule:
            def __init__(self, name, file=None):
                self.name = name
                if file:
                    self.__file__ = file

        return {"foo": FakeModule("foo", None), "bar": FakeModule("bar", "/bar/module.py")}

    @pytest.fixture
    def converter(self, fake_loaded_modules):
        LoadedModuleConverter._loaded_modules = fake_loaded_modules
        return LoadedModuleConverter()

    def test_correct_modules_returned(self, converter):
        expected_modules = {"foo": Module("foo", None), "bar": Module("bar", "/bar/module.py")}
        actual_modules = converter()
        assert actual_modules == expected_modules

    def test_repr(self, converter):
        assert repr(converter) == "LoadedModuleConverter()"
