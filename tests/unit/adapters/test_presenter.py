from repro.adapters.presenter import DJPresenter


def test_repr():
    assert repr(DJPresenter()) == "DJPresenter()"
