"""Contains reproducibility tools."""
from . import model
from .distribution import InstalledDistributionConverter
from .module import ActiveModuleConverter

model.get_installed_distributions = InstalledDistributionConverter()
model.get_active_modules = ActiveModuleConverter()
