"""Contains code related to classifying modules."""
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterator, Mapping

from .model import Module


class LoadedModuleConverter:
    """Converts loaded Python modules into module objects from the model."""

    _loaded_modules: Mapping[str, ModuleType] = sys.modules

    def __call__(self) -> dict[str, Module]:
        """Return a dictionary containing all loaded modules that are neither built-in nor namespaces."""
        return {nbm.__name__: Module(Path(nbm.__file__)) for nbm in self._non_namespace_modules}

    @property
    def _non_builtin_modules(self) -> Iterator[ModuleType]:
        for module in self._loaded_modules.values():
            if hasattr(module, "__file__"):
                yield module

    @property
    def _non_namespace_modules(self) -> Iterator[ModuleType]:
        for module in self._non_builtin_modules:
            if module.__file__ is not None:
                yield module

    def __repr__(self) -> str:
        """Return a string representation of the converter."""
        return f"{self.__class__.__name__}()"


get_loaded_modules = LoadedModuleConverter()
