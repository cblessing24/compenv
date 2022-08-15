"""Contains reproducibility tools."""
from .adapters.distribution import DistributionConverter
from .infrastructure.entrypoint import EnvironmentRecorder
from .model import record

record.get_distributions = DistributionConverter()

record_environment = EnvironmentRecorder()
