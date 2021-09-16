from pathlib import Path

import pytest

from repro.adapters.repository import DJComputationRecord, DJDistribution, DJMembership, DJModule
from repro.model import record as record_module
from repro.model.computation import ComputationRecord
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
def prepare_environment(installed_distributions, active_modules):
    def fake_get_active_modules():
        return iter(active_modules)

    def fake_get_installed_distributions():
        return iter(installed_distributions)

    record_module.get_active_modules = fake_get_active_modules
    record_module.get_installed_distributions = fake_get_installed_distributions


@pytest.fixture
def record(installed_distributions, active_modules):
    return Record(
        installed_distributions=installed_distributions,
        active_modules=active_modules,
    )


@pytest.fixture
def computation_record(record):
    return ComputationRecord("identifier", record)


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
def dj_memberships():
    return frozenset(
        [
            DJMembership(module_file="module1.py", distribution_name="dist1", distribution_version="0.1.0"),
            DJMembership(module_file="module2.py", distribution_name="dist2", distribution_version="0.1.1"),
        ]
    )


@pytest.fixture
def dj_comp_rec(dj_modules, dj_dists, dj_memberships):
    return DJComputationRecord(modules=dj_modules, distributions=dj_dists, memberships=dj_memberships)


@pytest.fixture
def fake_trigger():
    class FakeTrigger:
        triggered = False
        change_environment = False

        def __call__(self):
            if self.change_environment:
                self._change_environment()
            self.triggered = True

        def _change_environment(self):
            def fake_get_active_modules():
                return iter(frozenset())

            record_module.get_active_modules = fake_get_active_modules

        def __repr__(self):
            return f"{self.__class__.__name__}()"

    return FakeTrigger()
