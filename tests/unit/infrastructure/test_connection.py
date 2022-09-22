from unittest.mock import MagicMock

import pytest

from compenv.infrastructure.connection import ConnectionFacade, ConnectionFactory

from ..conftest import FakeConnection


class TestConnectionFacade:
    @staticmethod
    @pytest.fixture
    def connection_facade(fake_connection: FakeConnection) -> ConnectionFacade:
        return ConnectionFacade(fake_connection)

    @staticmethod
    def test_can_start_transaction(connection_facade: ConnectionFacade, fake_connection: FakeConnection) -> None:
        connection_facade.start()
        assert fake_connection.in_transaction

    @staticmethod
    def test_can_commit_transaction(connection_facade: ConnectionFacade, fake_connection: FakeConnection) -> None:
        connection_facade.commit()
        assert fake_connection.committed

    @staticmethod
    def test_can_rollback_transaction(connection_facade: ConnectionFacade, fake_connection: FakeConnection) -> None:
        connection_facade.start()
        connection_facade.rollback()
        assert not fake_connection.in_transaction

    @staticmethod
    def test_can_close_connection(connection_facade: ConnectionFacade, fake_connection: FakeConnection) -> None:
        connection_facade.close()
        assert not fake_connection.is_connected

    @staticmethod
    def test_repr(connection_facade: ConnectionFacade) -> None:
        assert repr(connection_facade) == "ConnectionFacade(connection=FakeConnection())"


class TestConnectionFactory:
    @staticmethod
    def test_returns_connection_facade(monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("compenv.infrastructure.connection.DJConnection", MagicMock)
        factory = ConnectionFactory(host="mydb", user="myuser", password="mypassword")
        assert isinstance(factory(), ConnectionFacade)

    @staticmethod
    def test_can_set_options(monkeypatch: pytest.MonkeyPatch) -> None:
        dj_connection_cls_mock = MagicMock()
        monkeypatch.setattr("compenv.infrastructure.connection.DJConnection", dj_connection_cls_mock)
        factory = ConnectionFactory(
            host="mydb", user="myuser", password="mypassword", options={"port": 1234, "init_fun": None, "use_tls": None}
        )
        factory()
        assert dj_connection_cls_mock.call_args_list[0].kwargs["port"] == 1234

    @staticmethod
    def test_repr() -> None:
        factory = ConnectionFactory(host="mydb", user="myuser", password="mypassword")
        assert repr(factory) == (
            "ConnectionFactory(host='mydb', user='myuser', password='mypassword', "
            "options={'port': None, 'init_fun': None, 'use_tls': None})"
        )
