import os
import subprocess
import time
from contextlib import contextmanager

import datajoint as dj
import docker
import pytest
from datajoint import Computed, Manual

from compenv import record_environment

pytestmark = pytest.mark.slow

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


@pytest.fixture
def manual_table_cls(schema):
    @schema
    class MyManualTable(Manual):
        definition = """
        id: int
        ---
        number: float
        """

    return MyManualTable


@pytest.fixture
def computed_table_cls(schema, manual_table_cls):
    @record_environment(schema)
    class MyComputedTable(Computed):
        definition = """
        -> manual_table_cls
        ---
        number: float
        """

        def make(self, key):
            number = (manual_table_cls & key).fetch1("number")
            key["number"] = number + 1

            self.insert1(key)

    return MyComputedTable


def test_records_do_not_differ(manual_table_cls, computed_table_cls, capsys):
    manual_table_cls().insert([{"id": 0, "number": 12.5}, {"id": 1, "number": 18}])
    computed_table_cls().populate()
    computed_table_cls().records.diff({"id": 0}, {"id": 1})
    captured = capsys.readouterr()
    assert captured.out == "The computation records do not differ\n"


@contextmanager
def installed_package(package, version):
    subprocess.run(["pip", "install", f"{package}=={version}"], check=True)
    try:
        yield
    finally:
        subprocess.run(["pip", "uninstall", "--yes", package], check=True)


def test_records_differ(manual_table_cls, computed_table_cls, capsys):
    manual_table_cls().insert([{"id": 0, "number": 12.5}])
    computed_table_cls().populate()
    manual_table_cls().insert([{"id": 1, "number": 18}])
    with installed_package("dummy_test", version="0.1.3"):
        computed_table_cls().populate()
    computed_table_cls().records.diff({"id": 0}, {"id": 1})
    captured = capsys.readouterr()
    assert captured.out == "The computation records differ\n"
