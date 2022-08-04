from types import FrameType
from typing import Any, Mapping, Optional, Type, cast

import pytest

from compenv.infrastructure.entrypoint import EnvironmentRecorder
from compenv.infrastructure.factory import DJTableFactory
from compenv.infrastructure.types import AutopopulatedTable, Schema

from ..conftest import FakeAutopopulatedTable, FakeTable


class FakeFrame:
    def __init__(self, f_back: Optional["FakeFrame"] = None, f_locals: Optional[Mapping[str, Any]] = None) -> None:
        self.f_back = f_back
        if f_locals:
            self.f_locals = f_locals
        else:
            self.f_locals = {}


@pytest.fixture
def fake_current_frame() -> FrameType:
    return cast(FrameType, FakeFrame(f_back=FakeFrame()))


class FakeCurrentFrameGetter:
    def __init__(self, frame: Optional[FrameType] = None) -> None:
        self.frame = frame

    def __call__(self) -> Optional[FrameType]:
        return self.frame


@pytest.fixture
def fake_get_current_frame(fake_current_frame: FrameType) -> FakeCurrentFrameGetter:

    return FakeCurrentFrameGetter(frame=fake_current_frame)


@pytest.fixture
def record_environment(fake_get_current_frame: FakeCurrentFrameGetter) -> EnvironmentRecorder:
    return EnvironmentRecorder(get_current_frame=fake_get_current_frame)


def test_schema_is_applied_to_table_class(
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    bla = record_environment(fake_schema)(fake_autopopulated_table)
    assert hasattr(bla, "database")


def test_locals_are_added_to_context_if_schema_has_no_context(
    fake_current_frame: FakeFrame,
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    assert fake_current_frame.f_back is not None
    fake_current_frame.f_back.f_locals = {"foo": "bar"}
    fake_autopopulated_table = record_environment(fake_schema)(fake_autopopulated_table)
    assert "foo" in fake_schema.context


def test_locals_are_not_added_to_context_if_schema_has_context(
    fake_current_frame: FakeFrame,
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    assert fake_current_frame.f_back is not None
    fake_current_frame.f_back.f_locals = {"foo": "bar"}
    fake_schema.context = {"baz": FakeTable}
    fake_autopopulated_table = record_environment(fake_schema)(fake_autopopulated_table)
    assert "foo" not in fake_schema.context


def test_raises_error_if_stack_frame_support_is_missing(
    fake_get_current_frame: FakeCurrentFrameGetter,
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    fake_get_current_frame.frame = None
    with pytest.raises(RuntimeError, match="Need stack frame support"):
        record_environment(fake_schema)(fake_autopopulated_table)


def test_raises_error_if_there_is_no_previous_frame(
    fake_current_frame: FakeFrame,
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    fake_current_frame.f_back = None
    with pytest.raises(RuntimeError, match="No previous"):
        record_environment(fake_schema)(fake_autopopulated_table)


def test_sets_records_attribute_on_table_class(
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    fake_autopopulated_table = record_environment(fake_schema)(fake_autopopulated_table)
    assert hasattr(fake_autopopulated_table, "records")


def test_records_attribute_is_table_factory(
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    fake_autopopulated_table = record_environment(fake_schema)(fake_autopopulated_table)
    assert isinstance(fake_autopopulated_table.records, DJTableFactory)  # type: ignore[attr-defined]


def test_table_factory_has_correct_schema(
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    fake_autopopulated_table = record_environment(fake_schema)(fake_autopopulated_table)
    assert fake_autopopulated_table.records.schema is fake_schema  # type: ignore[attr-defined]


def test_table_factory_has_correct_parent(
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[AutopopulatedTable],
) -> None:
    fake_autopopulated_table = record_environment(fake_schema)(fake_autopopulated_table)
    assert fake_autopopulated_table.records.parent == fake_autopopulated_table.__name__  # type: ignore[attr-defined]


def test_record_table_is_created(
    record_environment: EnvironmentRecorder,
    fake_schema: Schema,
    fake_autopopulated_table: Type[FakeAutopopulatedTable],
) -> None:
    fake_autopopulated_table = record_environment(fake_schema)(fake_autopopulated_table)
    assert fake_autopopulated_table.database == "schema"
