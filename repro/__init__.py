"""Contains reproducibility tools."""
from . import model
from .adapters.distribution import InstalledDistributionConverter
from .adapters.module import ActiveModuleConverter

model.get_installed_distributions = InstalledDistributionConverter()
model.get_active_modules = ActiveModuleConverter()
