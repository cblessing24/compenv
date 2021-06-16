"""Contains reproducibility tools."""
from . import model
from .distribution import InstalledDistributionConverter
from .module import LoadedModuleConverter

model.get_installed_distributions = InstalledDistributionConverter()
model.get_loaded_modules = LoadedModuleConverter()
