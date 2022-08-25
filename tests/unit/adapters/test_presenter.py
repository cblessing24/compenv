from __future__ import annotations

import pytest

from compenv.adapters.presenter import PrintingPresenter
from compenv.service.diff import DiffResponse


class FakePrinter:
    def __init__(self) -> None:
        self.texts: list[str] = []

    def __call__(self, text: str) -> None:
        self.texts.append(text)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


@pytest.fixture
def fake_printer() -> FakePrinter:
    return FakePrinter()


@pytest.fixture
def presenter(fake_printer: FakePrinter) -> PrintingPresenter:
    return PrintingPresenter(fake_printer)


@pytest.mark.parametrize(
    "differ,expected",
    [
        (True, "The computation records differ"),
        (False, "The computation records do not differ"),
    ],
)
def test_information_in_diff_response_is_correctly_printed(
    presenter: PrintingPresenter, fake_printer: FakePrinter, differ: bool, expected: str
) -> None:
    response = DiffResponse(differ=differ)
    presenter.diff(response)
    assert fake_printer.texts == [expected]


def test_repr(presenter: PrintingPresenter) -> None:
    assert repr(presenter) == "PrintingPresenter(print=FakePrinter())"
