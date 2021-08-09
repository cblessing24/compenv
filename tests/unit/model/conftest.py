from pathlib import Path

import pytest

from repro.model import record as record_module
from repro.model.environment import Environment
from repro.model.record import (
    ActiveDistributions,
    ActiveModules,
    Distribution,
    InstalledDistributions,
    Module,
    Modules,
    Record,
)


@pytest.fixture
def active_distributions():
    return ActiveDistributions(
        {Distribution("dist2", "0.1.1", modules=Modules({Module(Path("module2.py"), is_active=True)}))}
    )


@pytest.fixture
def installed_distributions(active_distributions):
    return InstalledDistributions(
        {
            Distribution("dist1", "0.1.0", modules=Modules({Module(Path("module1.py"), is_active=False)})),
        }.union(active_distributions)
    )


@pytest.fixture
def active_modules():
    return ActiveModules({Module(Path("module2.py"), is_active=True)})


@pytest.fixture
def record(installed_distributions, active_modules):
    return Record(
        installed_distributions=installed_distributions,
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
