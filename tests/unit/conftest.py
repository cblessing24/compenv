from pathlib import Path

import pytest

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
