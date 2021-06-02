from pathlib import Path

import pytest

from repro.hierarchy import Hierarchy, create_hierarchy, create_packages
from repro.model import Module, Package


@pytest.fixture
def paths():
    return {
        Path("/src/dist/foo/__init__.py"),
        Path("/src/dist/foo/module1.py"),
        Path("/src/dist/foo/module2.py"),
        Path("/src/dist/foo/bar/__init__.py"),
        Path("/src/dist/foo/bar/module3.py"),
        Path("/src/dist/foo/bar/module4.py"),
        Path("/src/dist/kappa/__init__.py"),
        Path("/src/dist/kappa/module5.py"),
    }


@pytest.fixture
def hierarchy():
    return Hierarchy(
        sub_hierarchies={
            Path("/src/dist/foo/__init__.py"): Hierarchy(
                module_paths={Path("/src/dist/foo/module1.py"), Path("/src/dist/foo/module2.py")},
                sub_hierarchies={
                    Path("/src/dist/foo/bar/__init__.py"): Hierarchy(
                        module_paths={Path("/src/dist/foo/bar/module3.py"), Path("/src/dist/foo/bar/module4.py")}
                    )
                },
            ),
            Path("/src/dist/kappa/__init__.py"): Hierarchy(module_paths={Path("/src/dist/kappa/module5.py")}),
        }
    )


def test_correct_hierarchy_is_created(paths, hierarchy):
    assert create_hierarchy(paths) == hierarchy


def test_paths_are_not_modified_in_place(paths):
    orig_paths = paths.copy()
    create_hierarchy(paths)
    assert paths == orig_paths


@pytest.fixture
def package():
    return {
        Package(
            "foo",
            file="/src/dist/foo/__init__.py",
            units=frozenset(
                {
                    Module("module1", file="/src/dist/foo/module1.py"),
                    Module("module2", file="/src/dist/foo/module2.py"),
                    Package(
                        "bar",
                        file="/src/dist/foo/bar/__init__.py",
                        units=frozenset(
                            {
                                Module("module3", file="/src/dist/foo/bar/module3.py"),
                                Module("module4", file="/src/dist/foo/bar/module4.py"),
                            }
                        ),
                    ),
                }
            ),
        ),
        Package(
            "kappa",
            file="/src/dist/kappa/__init__.py",
            units=frozenset({Module("module5", file="/src/dist/kappa/module5.py")}),
        ),
    }


def test_correct_packages_are_created_from_hierarchy(hierarchy, package):
    assert create_packages(hierarchy) == package
