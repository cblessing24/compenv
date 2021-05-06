import pytest

from repro.hook import add_hooks_to_make_method


@pytest.fixture
def hook_cls():
    class Hook:
        def __init__(self, name):
            self.name = name
            self.call = None
            self.raise_error = False

        def __call__(self, table, key):
            if self.raise_error:
                raise RuntimeError
            self.call = (table, key)

        def __repr__(self):
            return self.name

    return Hook


@pytest.fixture
def pre_hook(hook_cls):
    return hook_cls("pre_hook")


@pytest.fixture
def post_hook(hook_cls):
    return hook_cls("post_hook")


@pytest.fixture
def hooked_table(pre_hook, post_hook):
    class Table:
        def __init__(self):
            self.make_was_called = False
            self.raise_error = False

        def make(self, key):
            if self.raise_error:
                raise RuntimeError
            self.make_was_called = True

    hooked_table = add_hooks_to_make_method(pre_hook, post_hook)(Table)
    return hooked_table()


def test_if_call_to_pre_hook_is_correct(hooked_table, pre_hook):
    hooked_table.make("key")
    assert pre_hook.call == (hooked_table, "key")


def test_if_make_method_gets_called(hooked_table):
    hooked_table.make("key")
    assert hooked_table.make_was_called


def test_if_call_to_post_hook_is_correct(hooked_table, post_hook):
    hooked_table.make("key")
    assert post_hook.call == (hooked_table, "key")


def test_if_pre_hook_gets_called_before_post_hook(hooked_table, pre_hook, post_hook):
    pre_hook.raise_error = True
    with pytest.raises(RuntimeError):
        hooked_table.make("key")
    assert not post_hook.call


def test_if_pre_hook_gets_called_before_make_method(hooked_table, pre_hook):
    pre_hook.raise_error = True
    with pytest.raises(RuntimeError):
        hooked_table.make("key")
    assert not hooked_table.make_was_called


def test_if_make_method_gets_called_before_post_hook(hooked_table, post_hook):
    hooked_table.raise_error = True
    with pytest.raises(RuntimeError):
        hooked_table.make("key")
    assert not post_hook.call
