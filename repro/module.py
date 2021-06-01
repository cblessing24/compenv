"""Contains code related to classifying modules."""
import os
import sys
from types import ModuleType
from typing import Mapping

from .model import Module


def is_built_in_module(module: ModuleType) -> bool:
    """Return true if the module is built-in, false otherwise."""
    if module.__spec__ is None:
        return False
    return module.__spec__.origin == "built-in"


def is_bundled_module(module: ModuleType) -> bool:
    """Return true if the module is bundled with Python, false otherwise."""
    try:
        module_dir = os.path.dirname(module.__file__)
    except AttributeError:
        return False
    stdlib_dir = os.path.join(sys.prefix, sys.platlibdir, f"python{sys.version_info.major}.{sys.version_info.minor}")
    return module_dir == stdlib_dir


def is_stdlib_module(module: ModuleType) -> bool:
    """Return true if the module belongs to the standard library, false otherwise."""
    return is_built_in_module(module) or is_bundled_module(module)


class LoadedModuleConverter:
    """Converts loaded Python modules into module objects from the model."""

    _loaded_modules: Mapping[str, ModuleType] = sys.modules

    def __call__(self) -> dict[str, Module]:
        """Return a dictionary containing all loaded modules."""
        conv_modules: dict[str, Module] = {}
        for name, orig_module in self._loaded_modules.items():
            try:
                conv_module = Module(name, file=orig_module.__file__)
            except AttributeError:
                conv_module = Module(name, file=None)
            conv_modules[name] = conv_module
        return conv_modules

    def __repr__(self) -> str:
        """Return a string representation of the converter."""
        return f"{self.__class__.__name__}()"


get_loaded_modules = LoadedModuleConverter()
