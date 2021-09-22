import pytest

from repro.infrastructure.entrypoint import EnvironmentRecorder
from repro.infrastructure.factory import RecordTableFactory


class Frame:
    def __init__(self, f_back=None, f_locals=None):
        self.f_back = f_back
        if f_locals:
            self.f_locals = f_locals
        else:
            self.f_locals = {}


@pytest.fixture
def fake_current_frame():
    return Frame(f_back=Frame())


@pytest.fixture
def fake_get_current_frame(fake_current_frame):
    class FakeCurrentFrameGetter:
        def __init__(self, frame):
            self.frame = frame

        def __call__(self):
            return self.frame

    return FakeCurrentFrameGetter(frame=fake_current_frame)


@pytest.fixture
def record_environment(fake_get_current_frame):
    return EnvironmentRecorder(get_current_frame=fake_get_current_frame)


@pytest.fixture
def fake_connection():
    class FakeConnection:
        def __init__(self):
            self.in_transaction = None

        def cancel_transaction(self):
            self.in_transaction = False

    return FakeConnection()


@pytest.fixture
def fake_schema(fake_connection):
    class FakeSchema:
        def __init__(self, schema_name, connection):
            self.database = schema_name
            self.connection = connection
            self.context = None

        def __call__(self, table_cls, context=None):
            if context:
                self.context = context
            table_cls.database = self.database
            table_cls.connection = self.connection
            return table_cls

    return FakeSchema("schema", fake_connection)


@pytest.fixture
def fake_table_cls():
    class FakeTable:
        def make(self, key):
            pass

    return FakeTable


def test_schema_is_applied_to_table_class(record_environment, fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema)(fake_table_cls)
    assert hasattr(fake_table_cls, "database")


def test_locals_are_added_to_context_if_schema_has_no_context(
    fake_current_frame, record_environment, fake_schema, fake_table_cls
):
    fake_current_frame.f_back.f_locals = {"foo": "bar"}
    fake_table_cls = record_environment(fake_schema)(fake_table_cls)
    assert "foo" in fake_schema.context


def test_locals_are_not_added_to_context_if_schema_has_context(
    fake_current_frame, record_environment, fake_schema, fake_table_cls
):
    fake_current_frame.f_back.f_locals = {"foo": "bar"}
    fake_schema.context = {"baz": 10}
    fake_table_cls = record_environment(fake_schema)(fake_table_cls)
    assert "foo" not in fake_schema.context


def test_raises_error_if_stack_frame_support_is_missing(
    fake_get_current_frame, record_environment, fake_schema, fake_table_cls
):
    fake_get_current_frame.frame = None
    with pytest.raises(RuntimeError, match="Need stack frame support"):
        record_environment(fake_schema)(fake_table_cls)


def test_raises_error_if_there_is_no_previous_frame(
    fake_current_frame, record_environment, fake_schema, fake_table_cls
):
    fake_current_frame.f_back = None
    with pytest.raises(RuntimeError, match="No previous"):
        record_environment(fake_schema)(fake_table_cls)


def test_sets_records_attribute_on_table_class(record_environment, fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema)(fake_table_cls)
    assert hasattr(fake_table_cls, "records")


def test_records_attribute_is_table_factory(record_environment, fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema)(fake_table_cls)
    assert isinstance(fake_table_cls.records, RecordTableFactory)


def test_table_factory_has_correct_schema(record_environment, fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema)(fake_table_cls)
    assert fake_table_cls.records.schema is fake_schema


def test_table_factory_has_correct_parent(record_environment, fake_schema, fake_table_cls):
    fake_table_cls = record_environment(fake_schema)(fake_table_cls)
    assert fake_table_cls.records.parent == fake_table_cls


# def test_transaction_is_cancelled_when_make_method_is_called(
#     record_environment, fake_schema, fake_table_cls, fake_connection
# ):
#     fake_connection.in_transaction = True
#     fake_table_cls = record_environment(fake_schema)(fake_table_cls)
#     fake_table_cls().make({})
#     assert fake_connection.in_transaction is False
