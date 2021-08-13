import pytest

from repro.model import record as record_module
from repro.model.environment import Environment


@pytest.fixture
def environment(installed_distributions, active_modules):
    def fake_get_active_modules():
        return iter(active_modules)

    def fake_get_installed_distributions():
        return iter(installed_distributions)

    record_module.get_active_modules = fake_get_active_modules
    record_module.get_installed_distributions = fake_get_installed_distributions
    return Environment()
