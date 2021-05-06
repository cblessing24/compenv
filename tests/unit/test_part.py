import pytest
from datajoint import Part

from repro.part import add_part_table


@pytest.fixture
def part_table_name():
    return "MyPartTable"


@pytest.fixture
def part_table_definition():
    return "-> master"


@pytest.fixture
def table_cls(part_table_name, part_table_definition):
    @add_part_table(part_table_name, part_table_definition)
    class MyTable:
        pass

    return MyTable


def test_if_attribute_name_is_correct(table_cls, part_table_name):
    assert hasattr(table_cls, part_table_name)


def test_if_attribute_value_is_subclass_of_part_table(table_cls, part_table_name):
    assert issubclass(getattr(table_cls, part_table_name), Part)


def test_if_part_table_name_is_correct(table_cls, part_table_name):
    assert getattr(table_cls, part_table_name).__name__ == part_table_name


def test_if_part_table_definition_is_correct(table_cls, part_table_name, part_table_definition):
    assert getattr(table_cls, part_table_name).definition == part_table_definition
