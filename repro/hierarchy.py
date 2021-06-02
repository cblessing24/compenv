"""Contains code related to hierarchies of Python files."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, NewType

from repro.model import ModularUnit, Module, Package

InitPath = NewType("InitPath", Path)
ModulePath = NewType("ModulePath", Path)


@dataclass
class Hierarchy:
    """Represents a package/module hierarchy of Python file paths."""

    module_paths: set[ModulePath] = field(default_factory=set)
    sub_hierarchies: dict[InitPath, "Hierarchy"] = field(default_factory=dict)


def create_hierarchy(paths: Iterable[Path]) -> Hierarchy:
    """Recursively create a package/module hierarchy from an iterable of Python file paths."""
    hierarchy = Hierarchy()
    init_paths = {InitPath(p) for p in paths if p.name == "__init__.py"}
    if not init_paths:
        hierarchy.module_paths.update({ModulePath(p) for p in paths})
        return hierarchy
    top_level_depth = min(len(ip.parts) for ip in init_paths)
    top_level_init_paths = {ip for ip in init_paths if len(ip.parts) == top_level_depth}
    remaining_paths = set(paths) - top_level_init_paths
    for path in remaining_paths:
        if path in init_paths:
            continue
        if len(path.parts) == top_level_depth - 1:
            hierarchy.module_paths.add(ModulePath(path))
    remaining_paths -= hierarchy.module_paths
    for init_path in top_level_init_paths:
        sub_hierarchy_paths = {rp for rp in remaining_paths if rp.is_relative_to(init_path.parent)}
        hierarchy.sub_hierarchies[init_path] = create_hierarchy(sub_hierarchy_paths)
    return hierarchy


def create_packages(hierarchy: Hierarchy) -> set[Package]:
    """Recursively create packages from a hierarchy of Python files."""
    hierarchy.module_paths.clear()
    packages: set[Package] = set()
    for init_path, sub_hierarchy in hierarchy.sub_hierarchies.items():
        units: set[ModularUnit] = {Module(mp.stem, str(mp)) for mp in sub_hierarchy.module_paths}
        units.update(create_packages(sub_hierarchy))
        packages.add(Package(init_path.parent.name, file=str(init_path), units=frozenset(units)))
    return packages
