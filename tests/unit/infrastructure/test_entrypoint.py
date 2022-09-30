from typing import Any, Callable, Mapping, Optional, Type

import pytest

from compenv.infrastructure.entrypoint import determine_context, replaced_connection_table
from compenv.infrastructure.types import FrameType

from ..conftest import FakeAutopopulatedTable, FakeConnection, FakeTable


class FakeFrame:
    def __init__(self, f_back: Optional["FakeFrame"] = None, f_locals: Optional[Mapping[str, Any]] = None) -> None:
        self.f_back = f_back
        if f_locals:
            self.f_locals = dict(f_locals)
        else:
            self.f_locals = {}


@pytest.fixture
def fake_current_frame() -> FrameType:
    return FakeFrame(f_back=FakeFrame())


class FakeCurrentFrameGetter:
    def __init__(self, frame: Optional[FrameType] = None) -> None:
        self.frame = frame

    def __call__(self) -> Optional[FrameType]:
        return self.frame


def test_locals_are_added_to_context_if_schema_has_no_context(
    fake_current_frame: FakeFrame,
) -> None:
    assert fake_current_frame.f_back is not None
    fake_current_frame.f_back.f_locals = {"foo": "bar"}
    context = determine_context({}, fake_current_frame)
    assert "foo" in context


def test_locals_are_not_added_to_context_if_schema_has_context(
    fake_current_frame: FakeFrame,
) -> None:
    assert fake_current_frame.f_back is not None
    fake_current_frame.f_back.f_locals = {"foo": "bar"}
    context = determine_context({"baz": FakeTable}, fake_current_frame)
    assert "foo" not in context


def test_raises_error_if_stack_frame_support_is_missing() -> None:
    with pytest.raises(RuntimeError, match="Need stack frame support"):
        determine_context({}, None)


def test_raises_error_if_there_is_no_previous_frame(
    fake_current_frame: FakeFrame,
) -> None:
    fake_current_frame.f_back = None
    with pytest.raises(RuntimeError, match="No previous"):
        determine_context({}, fake_current_frame)


def test_context_is_based_on_previous_stack_frame(fake_current_frame: FakeFrame) -> None:
    assert fake_current_frame.f_back is not None
    fake_current_frame.f_back.f_locals["something"] = "else"
    context = determine_context({}, fake_current_frame)
    assert context["something"] == "else"


class TestReplacedConnectionTable:
    @staticmethod
    def test_connection_is_replaced(
        fake_autopopulated_table: Type[FakeAutopopulatedTable], create_fake_connection: Callable[[], FakeConnection]
    ) -> None:
        fake_autopopulated_table.connection = create_fake_connection()
        temp_connection = create_fake_connection()
        with replaced_connection_table(fake_autopopulated_table(), temp_connection):
            assert fake_autopopulated_table.connection is temp_connection

    @staticmethod
    def test_original_connection_is_restored(
        fake_autopopulated_table: Type[FakeAutopopulatedTable], create_fake_connection: Callable[[], FakeConnection]
    ) -> None:
        original_connection = create_fake_connection()
        fake_autopopulated_table.connection = original_connection
        with replaced_connection_table(fake_autopopulated_table(), create_fake_connection()):
            pass
        assert fake_autopopulated_table.connection is original_connection
