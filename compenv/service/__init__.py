"""This package contains all use-cases."""
from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from typing import Any, Type, TypeVar

from .abstract import Service

SERVICE_CLASSES = {}


_T = TypeVar("_T", bound=Service[Any, Any])


def register_service_class(service_class: Type[_T]) -> Type[_T]:
    """Add the service class to the services dictionary."""
    SERVICE_CLASSES[service_class.name] = service_class
    return service_class


def initialize_services(
    service_classes: Mapping[str, Type[_T]],
    output_ports: Mapping[str, Callable[[Any], None]],
    dependencies: Mapping[str, object],
) -> Mapping[str, _T]:
    """Initialize the services."""
    initialized_services = {}
    for name, service_class in service_classes.items():
        init_parameters = list(inspect.signature(service_class.__init__).parameters)
        service_class_dependencies = {name: dep for name, dep in dependencies.items() if name in init_parameters}
        initialized_services[name] = service_class(output_port=output_ports[name], **service_class_dependencies)
    return initialized_services
