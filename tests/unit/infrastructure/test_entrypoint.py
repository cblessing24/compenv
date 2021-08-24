import pytest

from repro.infrastructure.entrypoint import record_environment
from repro.infrastructure.factory import RecordTableFactory


@pytest.fixture
def fake_schema():
    class FakeConnection:
        def __init__(self, schema):
            self.schemas = {schema.database: schema}

    class FakeSchema:
        def __init__(self, database):
            self.database = database

        def __call__(self, table_cls):
            table_cls.database = self.database
            table_cls.connection = FakeConnection(self)
            return table_cls

    return FakeSchema("schema")


@pytest.fixture
def fake_table_cls():
    class FakeTable:
        def make(self, key):
            pass

    return FakeTable


def test_raises_error_if_schema_decorator_not_applied_first(fake_table_cls):
    with pytest.raises(ValueError, match="Schema decorator must be applied before applying this decorator!"):
        record_environment(fake_table_cls)


def test_sets_records_attribute_on_table_class(fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema(fake_table_cls))
    assert hasattr(fake_table_cls, "records")


def test_records_attribute_is_table_factory(fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema(fake_table_cls))
    assert isinstance(fake_table_cls.records, RecordTableFactory)


def test_table_factory_has_correct_schema(fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema(fake_table_cls))
    assert fake_table_cls.records.schema is fake_schema


def test_table_factory_has_correct_parent(fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema(fake_table_cls))
    assert fake_table_cls.records.parent == fake_table_cls.__name__
