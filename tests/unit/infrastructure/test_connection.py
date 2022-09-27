from unittest.mock import MagicMock

import pytest

from compenv.infrastructure.connection import ConnectionFacade, ConnectionFactory

from ..conftest import FakeConnection


class FakeConnectionFactory:
    def __init__(self, fake_connection: FakeConnection) -> None:
        self._fake_connection = fake_connection

    def __call__(self) -> FakeConnection:
        return self._fake_connection

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(fake_connection={self._fake_connection})"


@pytest.fixture
def fake_connection_factory(fake_connection: FakeConnection) -> FakeConnectionFactory:
    return FakeConnectionFactory(fake_connection)


class TestConnectionFacade:
    @staticmethod
    @pytest.fixture
    def connection_facade(fake_connection_factory: FakeConnectionFactory) -> ConnectionFacade:
        return ConnectionFacade(fake_connection_factory)

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
    def test_can_open_connection(connection_facade: ConnectionFacade) -> None:
        connection_facade.open()
        assert connection_facade.dj_connection

    @staticmethod
    def test_repr(connection_facade: ConnectionFacade) -> None:
        assert (
            repr(connection_facade)
            == "ConnectionFacade(factory=FakeConnectionFactory(fake_connection=FakeConnection()))"
        )


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
    def test_can_access_connection(connection_factory: ConnectionFactory) -> None:
        connection_factory()
        assert connection_factory.dj_connection == "DataJoint Connection"  # type: ignore[comparison-overlap]

    @staticmethod
    def test_raises_runtime_error_if_no_connection(connection_factory: ConnectionFactory) -> None:
        with pytest.raises(RuntimeError, match="is missing"):
            connection_factory.dj_connection

    @staticmethod
    def test_repr(
        connection_factory: ConnectionFactory,
    ) -> None:
        assert repr(connection_factory) == (
            "ConnectionFactory(host='mydb', user='myuser', password='mypassword', "
            "options={'port': None, 'init_fun': None, 'use_tls': None})"
        )
