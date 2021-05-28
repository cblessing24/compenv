import pytest

from repro.model import Distribution, Module


@pytest.fixture
def distribution():
    return Distribution("bar", "0.1.0", {Module("module", "/foo/module.py")})


def test_non_module_object_not_in_distribution(distribution):
    assert object not in distribution


def test_module_in_distribution_if_module_in_distribution_modules(distribution):
    module = Module("module", "/foo/module.py")
    assert module in distribution


def test_module_not_in_distribution_if_module_not_in_distribution_modules(distribution):
    module = Module("foo", "/bar/module.py")
    assert module not in distribution


def test_length_equal_to_number_of_modules_in_distribution(distribution):
    assert len(distribution) == 1


def test_iterating_distribution_iterates_modules(distribution):
    assert next(iter(distribution)) == Module("module", "/foo/module.py")
