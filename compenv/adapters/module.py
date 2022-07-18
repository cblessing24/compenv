"""Contains code related to classifying modules."""
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Mapping

from ..model.record import ActiveModules, Module


class ActiveModuleConverter:
    """Converts active Python modules into module objects from the model."""

    _active_modules: Mapping[str, ModuleType] = sys.modules

    @lru_cache
    def __call__(self) -> ActiveModules:
        """Return a dictionary containing all active modules that are neither built-in nor namespaces."""
        modules = []
        for module in self._active_modules.values():
            if file := getattr(module, "__file__", None):
                modules.append(Module(Path(file), is_active=True))
        return ActiveModules(modules)

    def __repr__(self) -> str:
        """Return a string representation of the converter."""
        return f"{self.__class__.__name__}()"
