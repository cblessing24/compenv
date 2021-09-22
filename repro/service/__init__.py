"""This package contains all use-cases."""
from typing import Dict, Type

from .abstract import Service
from .record import RecordService

SERVICES: Dict[str, Type[Service]] = {"record": RecordService}
