"""Contains code related to classifying modules."""
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Iterator, Mapping

from ..model.record import ActiveModules, Module


class ActiveModuleConverter:
    """Converts active Python modules into module objects from the model."""

    _active_modules: Mapping[str, ModuleType] = sys.modules

    @lru_cache(maxsize=None)
    def __call__(self) -> ActiveModules:
        """Return a dictionary containing all active modules that are neither built-in nor namespaces."""
        return ActiveModules(Module(Path(nbm.__file__), is_active=True) for nbm in self._non_namespace_modules)

    @property
    def _non_builtin_modules(self) -> Iterator[ModuleType]:
        for module in self._active_modules.values():
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
