from pathlib import Path

import pytest

from repro.adapters.repository import DJComputationRecord, DJDistribution, DJModule, DJModuleAffiliation
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
def primary():
    return {"a": 0, "b": 1}


@pytest.fixture
def dj_modules():
    return frozenset(
        [
            DJModule(module_file="module1.py", module_is_active="False"),
            DJModule(module_file="module2.py", module_is_active="True"),
        ]
    )


@pytest.fixture
def dj_dists():
    return frozenset(
        [
            DJDistribution(distribution_name="dist1", distribution_version="0.1.0"),
            DJDistribution(distribution_name="dist2", distribution_version="0.1.1"),
        ]
    )


@pytest.fixture
def dj_module_affiliations():
    return frozenset(
        [
            DJModuleAffiliation(module_file="module1.py", distribution_name="dist1"),
            DJModuleAffiliation(module_file="module2.py", distribution_name="dist2"),
        ]
    )


@pytest.fixture
def dj_comp_rec(dj_modules, dj_dists, dj_module_affiliations):
    return DJComputationRecord(modules=dj_modules, distributions=dj_dists, module_affiliations=dj_module_affiliations)
