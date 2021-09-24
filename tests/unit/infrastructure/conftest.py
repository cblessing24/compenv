import pytest


@pytest.fixture
def fake_connection():
    class FakeConnection:
        def __init__(self):
            self.in_transaction = None

        def cancel_transaction(self):
            self.in_transaction = False

    return FakeConnection()


@pytest.fixture
def fake_parent():
    class FakeParent:
        def make(self, key):
            pass

    return FakeParent


@pytest.fixture
def fake_schema(fake_connection, fake_parent):
    class FakeSchema:
        schema_tables = {}

        def __init__(self, schema_name, connection):
            self.database = schema_name
            self.connection = connection
            self.table_cls = None
            self.context = None

        def __call__(self, table_cls, context=None):
            if context:
                self.context = context
            self.table_cls = table_cls
            table_cls.database = self.database
            table_cls.connection = self.connection
            return table_cls

        def spawn_missing_classes(self, context):
            context.update(self.schema_tables)

        def __repr__(self):
            return "FakeSchema()"

    FakeSchema.schema_tables[fake_parent.__name__] = fake_parent

    return FakeSchema("schema", fake_connection)
