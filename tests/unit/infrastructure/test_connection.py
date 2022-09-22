import pytest

from compenv.infrastructure.connection import ConnectionFacade

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
