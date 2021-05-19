"""Contains code related to classifying modules."""
import os
import sys
from types import ModuleType


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
