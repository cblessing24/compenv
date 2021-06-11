from pathlib import Path

import pytest

from repro.model import Module
from repro.module import LoadedModuleConverter


class TestLoadedModuleConverter:
    @staticmethod
    @pytest.fixture
    def fake_loaded_modules():
        class FakeModule:
            def __init__(self, name, file):
                self.__name__ = name
                if file == "<namespace>":
                    self.__file__ = None
                elif not file == "<builtin>":
                    self.__file__ = file

        return {
            "module": FakeModule("module", "/package/module.py"),
            "builtin": FakeModule("builtin", "<builtin>"),
            "package": FakeModule("package", "/package/__init__.py"),
            "namespace": FakeModule("namespace", "<namespace>"),
        }

    @staticmethod
    @pytest.fixture
    def converter(fake_loaded_modules):
        LoadedModuleConverter._loaded_modules = fake_loaded_modules
        return LoadedModuleConverter()

    @staticmethod
    def test_correct_modules_returned(converter):
        expected_modules = {
            "module": Module(Path("/package/module.py")),
            "package": Module(Path("/package/__init__.py")),
        }
        actual_modules = converter()
        assert actual_modules == expected_modules

    @staticmethod
    def test_repr(converter):
        assert repr(converter) == "LoadedModuleConverter()"
