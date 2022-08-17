"""Contains reproducibility tools."""
from .infrastructure.entrypoint import EnvironmentRecorder

record_environment = EnvironmentRecorder()
