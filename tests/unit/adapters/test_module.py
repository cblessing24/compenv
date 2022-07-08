from pathlib import Path

import pytest

from compenv.adapters.module import ActiveModuleConverter
from compenv.model.record import Module


class TestActiveModuleConverter:
    @staticmethod
    @pytest.fixture
    def fake_active_modules():
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
    def converter(fake_active_modules):
        ActiveModuleConverter._active_modules = fake_active_modules
        return ActiveModuleConverter()

    @staticmethod
    def test_correct_modules_returned(converter):
        expected_modules = frozenset(
            {
                Module(Path("/package/module.py"), is_active=True),
                Module(Path("/package/__init__.py"), is_active=True),
            }
        )
        actual_modules = converter()
        assert actual_modules == expected_modules

    @staticmethod
    def test_repr(converter):
        assert repr(converter) == "ActiveModuleConverter()"
