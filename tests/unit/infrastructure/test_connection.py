from typing import Optional
from unittest.mock import MagicMock

import pytest

from compenv.infrastructure.connection import Connection, DJConnectionFactory

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
    def connection(fake_connection_factory: FakeConnectionFactory) -> Connection:
        return Connection(fake_connection_factory)

    @staticmethod
    def test_raises_runtime_error_if_no_connection(connection: Connection) -> None:
        with pytest.raises(RuntimeError, match="Not connected"):
            connection.dj_connection

    @staticmethod
    def test_can_start_transaction(connection: Connection, fake_connection_factory: FakeConnectionFactory) -> None:
        with connection:
            connection.transaction.start()
            assert fake_connection_factory.fake_connection.in_transaction

    @staticmethod
    def test_can_commit_transaction(connection: Connection, fake_connection_factory: FakeConnectionFactory) -> None:
        with connection:
            connection.transaction.start()
            connection.transaction.commit()
            assert fake_connection_factory.fake_connection.committed

    @staticmethod
    def test_can_rollback_transaction(connection: Connection, fake_connection: FakeConnection) -> None:
        with connection:
            connection.transaction.start()
            connection.transaction.rollback()
            assert not fake_connection.in_transaction

    @staticmethod
    def test_can_close_connection(connection: Connection, fake_connection_factory: FakeConnectionFactory) -> None:
        with connection:
            pass
        assert not fake_connection_factory.fake_connection.is_connected

    @staticmethod
    def test_accessing_dj_connection_after_closing_raises_error(connection: Connection) -> None:
        with connection:
            pass
        with pytest.raises(RuntimeError, match="Not connected"):
            connection.dj_connection

    @staticmethod
    def test_can_open_connection(connection: Connection) -> None:
        with connection:
            assert connection.dj_connection

    @staticmethod
    def test_repr(connection: Connection) -> None:
        assert repr(connection) == "Connection(factory=FakeConnectionFactory())"


class TestConnectionFactory:
    @staticmethod
    @pytest.fixture
    def connection_factory() -> DJConnectionFactory:
        return DJConnectionFactory(host="mydb", user="myuser", password="mypassword")

    @staticmethod
    @pytest.fixture(autouse=True)
    def dj_connection_cls_mock(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        dj_connection_cls_mock = MagicMock(return_value="DataJoint Connection")
        monkeypatch.setattr("compenv.infrastructure.connection.DJConnection", dj_connection_cls_mock)
        return dj_connection_cls_mock

    @staticmethod
    def test_returns_connection(connection_factory: DJConnectionFactory) -> None:
        assert connection_factory() == "DataJoint Connection"  # type: ignore[comparison-overlap]

    @staticmethod
    def test_can_set_options(dj_connection_cls_mock: MagicMock) -> None:
        factory = DJConnectionFactory(
            host="mydb", user="myuser", password="mypassword", options={"port": 1234, "init_fun": None, "use_tls": None}
        )
        factory()
        assert dj_connection_cls_mock.call_args_list[0].kwargs["port"] == 1234

    @staticmethod
    def test_repr(
        connection_factory: DJConnectionFactory,
    ) -> None:
        assert repr(connection_factory) == (
            "DJConnectionFactory(host='mydb', user='myuser', password='mypassword', "
            "options={'port': None, 'init_fun': None, 'use_tls': None})"
        )
