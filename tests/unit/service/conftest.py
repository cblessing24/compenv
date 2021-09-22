import pytest


@pytest.fixture
def fake_output_port():
    class FakeOutputPort:
        def __init__(self):
            self.responses = []

        def __call__(self, response):
            self.responses.append(response)

    return FakeOutputPort()
