import pytest

from compenv.adapters.controller import DJController


@pytest.fixture
def fake_presenter():
    class FakePresenter:
        def __init__(self):
            self.responses = []

        def record(self, response):
            self.responses.append(response)

        def __repr__(self):
            return self.__class__.__name__ + "()"

    return FakePresenter()


@pytest.fixture
def controller(fake_repository, fake_translator, fake_presenter):
    return DJController(fake_repository, fake_translator, fake_presenter)


@pytest.fixture
def fake_make():
    class FakeMake:
        def __init__(self):
            self.calls = []

        def __call__(self, key):
            self.calls.append(key)

    return FakeMake()


def test_calling_record_calls_make_method_with_appropriate_key(controller, primary, fake_make):
    controller.record(primary, fake_make)
    assert fake_make.calls == [primary]


def test_calling_record_inserts_record_with_appropriate_identifier(
    controller, primary, fake_make, fake_repository, identifier
):
    controller.record(primary, fake_make)
    assert [cr.identifier for cr in fake_repository.values()] == [identifier]


def test_repr(controller):
    assert (
        repr(controller)
        == "DJController(repo=FakeRepository(), translator=FakeTranslator(), presenter=FakePresenter())"
    )
