import pytest
from pytest import CaptureFixture

from compenv.adapters.presenter import DJPresenter
from compenv.service.diff import DiffResponse


def test_repr() -> None:
    assert repr(DJPresenter()) == "DJPresenter()"


@pytest.mark.parametrize(
    "differ,expected",
    [
        (True, "The computation records differ\n"),
        (False, "The computation records do not differ\n"),
    ],
)
def test_information_in_diff_response_is_correctly_printed(
    capsys: CaptureFixture[str], differ: bool, expected: str
) -> None:
    response = DiffResponse(differ=differ)
    DJPresenter().diff(response)
    captured = capsys.readouterr()
    assert captured.out == expected
