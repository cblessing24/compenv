import pytest

from compenv.infrastructure.hook import hook_into_make_method


@pytest.fixture
def hook():
    class Hook:
        def __init__(self):
            self.args = None

        def __call__(self, *args):
            self.args = args

    return Hook()


@pytest.fixture
def original_make_method():
    def make(self, key):
        pass

    return make


@pytest.fixture
def table(hook, original_make_method):

    Table = type("Table", tuple(), {"make": original_make_method})
    table = hook_into_make_method(hook)(Table)
    return table()


def test_if_hook_gets_called_with_correct_arguments(table, hook, original_make_method):
    table.make("key")
    assert hook.args == (original_make_method, table, "key")
