from typing import List

import pytest

from compenv.service.abstract import Response


class FakeOutputPort:
    def __init__(self) -> None:
        self.responses: List[Response] = []

    def __call__(self, response: Response) -> None:
        self.responses.append(response)


@pytest.fixture
def fake_output_port() -> FakeOutputPort:
    return FakeOutputPort()
