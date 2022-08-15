"""Contains reproducibility tools."""
from .adapters.distribution import InstalledDistributionConverter
from .infrastructure.entrypoint import EnvironmentRecorder
from .model import record

record.get_installed_distributions = InstalledDistributionConverter()

record_environment = EnvironmentRecorder()
