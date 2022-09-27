from typing import Optional
from unittest.mock import MagicMock

import pytest

from compenv.infrastructure.connection import ConnectionFacade, ConnectionFactory

from ..conftest import FakeConnection


class FakeConnectionFactory:
    def __init__(self) -> None:
        self._fake_connection: Optional[FakeConnection] = None

    @property
    def fake_connection(self) -> FakeConnection:
        if not self._fake_connection:
            raise RuntimeError("No connection")
        return self._fake_connection

    def __call__(self) -> FakeConnection:
        self._fake_connection = FakeConnection()
        return self.fake_connection

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


@pytest.fixture
def fake_connection_factory() -> FakeConnectionFactory:
    return FakeConnectionFactory()


class TestConnectionFacade:
    @staticmethod
    @pytest.fixture
    def connection_facade(fake_connection_factory: FakeConnectionFactory) -> ConnectionFacade:
        return ConnectionFacade(fake_connection_factory)

    @staticmethod
    def test_raises_runtime_error_if_no_connection(connection_facade: ConnectionFacade) -> None:
        with pytest.raises(RuntimeError, match="Not connected"):
            connection_facade.dj_connection

    @staticmethod
    def test_can_start_transaction(
        connection_facade: ConnectionFacade, fake_connection_factory: FakeConnectionFactory
    ) -> None:
        connection_facade.open()
        connection_facade.start()
        assert fake_connection_factory.fake_connection.in_transaction

    @staticmethod
    def test_can_commit_transaction(
        connection_facade: ConnectionFacade, fake_connection_factory: FakeConnectionFactory
    ) -> None:
        connection_facade.open()
        connection_facade.commit()
        assert fake_connection_factory.fake_connection.committed

    @staticmethod
    def test_can_rollback_transaction(connection_facade: ConnectionFacade, fake_connection: FakeConnection) -> None:
        connection_facade.open()
        connection_facade.start()
        connection_facade.rollback()
        assert not fake_connection.in_transaction

    @staticmethod
    def test_can_close_connection(
        connection_facade: ConnectionFacade, fake_connection_factory: FakeConnectionFactory
    ) -> None:
        connection_facade.open()
        connection_facade.close()
        assert not fake_connection_factory.fake_connection.is_connected

    @staticmethod
    def test_accessing_dj_connection_after_closing_raises_error(connection_facade: ConnectionFacade) -> None:
        connection_facade.open()
        connection_facade.close()
        with pytest.raises(RuntimeError, match="Not connected"):
            connection_facade.dj_connection

    @staticmethod
    def test_can_open_connection(connection_facade: ConnectionFacade) -> None:
        connection_facade.open()
        assert connection_facade.dj_connection

    @staticmethod
    def test_repr(connection_facade: ConnectionFacade) -> None:
        assert repr(connection_facade) == "ConnectionFacade(factory=FakeConnectionFactory())"


class TestConnectionFactory:
    @staticmethod
    @pytest.fixture
    def connection_factory() -> ConnectionFactory:
        return ConnectionFactory(host="mydb", user="myuser", password="mypassword")

    @staticmethod
    @pytest.fixture(autouse=True)
    def dj_connection_cls_mock(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        dj_connection_cls_mock = MagicMock(return_value="DataJoint Connection")
        monkeypatch.setattr("compenv.infrastructure.connection.DJConnection", dj_connection_cls_mock)
        return dj_connection_cls_mock

    @staticmethod
    def test_returns_connection(connection_factory: ConnectionFactory) -> None:
        assert connection_factory() == "DataJoint Connection"  # type: ignore[comparison-overlap]

    @staticmethod
    def test_can_set_options(dj_connection_cls_mock: MagicMock) -> None:
        factory = ConnectionFactory(
            host="mydb", user="myuser", password="mypassword", options={"port": 1234, "init_fun": None, "use_tls": None}
        )
        factory()
        assert dj_connection_cls_mock.call_args_list[0].kwargs["port"] == 1234

    @staticmethod
    def test_repr(
        connection_factory: ConnectionFactory,
    ) -> None:
        assert repr(connection_factory) == (
            "ConnectionFactory(host='mydb', user='myuser', password='mypassword', "
            "options={'port': None, 'init_fun': None, 'use_tls': None})"
        )
