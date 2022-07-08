import os
import time

import datajoint as dj
import docker
import pytest
from datajoint import Computed, Manual

from compenv import record_environment

HEALTH_CHECK_MAX_RETRIES = 60
HEALTH_CHECK_INTERVAL = 1

DB_IMAGE_TAG = "8"
DB_HOST = "dj-mysql" if os.environ.get("DOCKER") else "localhost"
DB_USER = "root"
DB_PASSWORD = "simple"
DB_PORT = "3306"

SCHEMA_NAME = "compenv"


class ContainerRunner:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.container = None

    def __enter__(self):
        self._run_container()
        self._wait_until_healthy()
        return self.container

    def __exit__(self, type, value, traceback):
        self.container.stop()

    def _run_container(self):
        self.container = self.client.containers.run(**self.config)

    def _wait_until_healthy(self):
        n_tries = 0
        while True:
            self.container.reload()
            if self.container.attrs["State"]["Health"]["Status"] == "healthy":
                break
            if n_tries >= HEALTH_CHECK_MAX_RETRIES:
                self.container.stop()
                raise RuntimeError(
                    f"Container '{self.container.name}' not healthy "
                    f"after max number ({HEALTH_CHECK_MAX_RETRIES}) of retries"
                )
            time.sleep(HEALTH_CHECK_INTERVAL)
            n_tries += 1


@pytest.fixture
def docker_client():
    return docker.from_env()


@pytest.fixture
def start_database(docker_client):
    config = {
        "image": "datajoint/mysql:" + DB_IMAGE_TAG,
        "detach": True,
        "auto_remove": True,
        "name": "dj-mysql",
        "network": "compenv_test",
        "environment": {"MYSQL_ROOT_PASSWORD": DB_PASSWORD},
        "ports": {DB_PORT: DB_PORT},
    }
    with ContainerRunner(docker_client, config):
        yield


@pytest.fixture
def configure_dj():
    dj.config["database.host"] = DB_HOST
    dj.config["database.user"] = DB_USER
    dj.config["database.password"] = DB_PASSWORD


@pytest.fixture
def schema(start_database, configure_dj):
    return dj.schema(SCHEMA_NAME)


def test_record_is_added_to_record_table(schema):
    @schema
    class MyManualTable(Manual):
        definition = """
        id: int
        ---
        number: float
        """

    @record_environment(schema)
    class MyComputedTable(Computed):
        definition = """
        -> MyManualTable
        ---
        number: float
        """

        def make(self, key):
            number = (MyManualTable & key).fetch1("number")
            key["number"] = number + 1

            self.insert1(key)

    MyManualTable().insert([{"id": 0, "number": 12.5}, {"id": 1, "number": 18}])

    MyComputedTable().populate()

    assert len(MyComputedTable.records()) == 2
