"""Contains reproducibility tools."""
from .adapters.distribution import InstalledDistributionConverter
from .adapters.module import ActiveModuleConverter
from .model import record

record.get_installed_distributions = InstalledDistributionConverter()
record.get_active_modules = ActiveModuleConverter()
