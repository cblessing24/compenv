import pytest

from compenv.infrastructure.entrypoint import EnvironmentRecorder
from compenv.infrastructure.factory import DJTableFactory


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


def test_schema_is_applied_to_table_class(record_environment, fake_schema, fake_parent):
    fake_parent = record_environment(fake_schema)(fake_parent)
    assert hasattr(fake_parent, "database")


def test_locals_are_added_to_context_if_schema_has_no_context(
    fake_current_frame, record_environment, fake_schema, fake_parent
):
    fake_current_frame.f_back.f_locals = {"foo": "bar"}
    fake_parent = record_environment(fake_schema)(fake_parent)
    assert "foo" in fake_schema.context


def test_locals_are_not_added_to_context_if_schema_has_context(
    fake_current_frame, record_environment, fake_schema, fake_parent
):
    fake_current_frame.f_back.f_locals = {"foo": "bar"}
    fake_schema.context = {"baz": 10}
    fake_parent = record_environment(fake_schema)(fake_parent)
    assert "foo" not in fake_schema.context


def test_raises_error_if_stack_frame_support_is_missing(
    fake_get_current_frame, record_environment, fake_schema, fake_parent
):
    fake_get_current_frame.frame = None
    with pytest.raises(RuntimeError, match="Need stack frame support"):
        record_environment(fake_schema)(fake_parent)


def test_raises_error_if_there_is_no_previous_frame(fake_current_frame, record_environment, fake_schema, fake_parent):
    fake_current_frame.f_back = None
    with pytest.raises(RuntimeError, match="No previous"):
        record_environment(fake_schema)(fake_parent)


def test_sets_records_attribute_on_table_class(record_environment, fake_schema, fake_parent):
    fake_parent = record_environment(fake_schema)(fake_parent)
    assert hasattr(fake_parent, "records")


def test_records_attribute_is_table_factory(record_environment, fake_schema, fake_parent):
    fake_parent = record_environment(fake_schema)(fake_parent)
    assert isinstance(fake_parent.records, DJTableFactory)


def test_table_factory_has_correct_schema(record_environment, fake_schema, fake_parent):
    fake_parent = record_environment(fake_schema)(fake_parent)
    assert fake_parent.records.schema is fake_schema


def test_table_factory_has_correct_parent(record_environment, fake_schema, fake_parent):
    fake_parent = record_environment(fake_schema)(fake_parent)
    assert fake_parent.records.parent == fake_parent.__name__


def test_record_table_is_created(record_environment, fake_schema, fake_parent):
    fake_parent = record_environment(fake_schema)(fake_parent)
    assert "FakeParentRecord" in fake_schema.decorated_tables
