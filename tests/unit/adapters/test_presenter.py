from compenv.adapters.presenter import DJPresenter


def test_repr() -> None:
    assert repr(DJPresenter()) == "DJPresenter()"
