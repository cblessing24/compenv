import pytest

from repro.model import record as record_module
from repro.model.environment import Environment
from repro.model.record import Distribution, Module, Record


@pytest.fixture
def installed_distributions():
    return frozenset(
        {
            Distribution("dist1", "0.1.0", modules=frozenset({Module("module1.py")})),
            Distribution("dist2", "0.1.1", modules=frozenset({Module("module2.py")})),
        }
    )


@pytest.fixture
def active_modules():
    return frozenset({Module("module2.py")})


@pytest.fixture
def active_distributions():
    return frozenset({Distribution("dist2", "0.1.1", modules=frozenset({Module("module2.py")}))})


@pytest.fixture
def record(installed_distributions, active_modules, active_distributions):
    return Record(
        installed_distributions=installed_distributions,
        active_distributions=active_distributions,
        active_modules=active_modules,
    )


@pytest.fixture
def environment(installed_distributions, active_modules):
    def fake_get_active_modules():
        return iter(active_modules)

    def fake_get_installed_distributions():
        return iter(installed_distributions)

    record_module.get_active_modules = fake_get_active_modules
    record_module.get_installed_distributions = fake_get_installed_distributions
    return Environment()
