"""This package contains all use-cases."""
from __future__ import annotations

import inspect

SERVICE_CLASSES = {}


def register_service_class(service_class):  # type: ignore
    """Add the service class to the services dictionary."""
    SERVICE_CLASSES[service_class.name] = service_class
    return service_class


def initialize_services(service_classes, output_ports, dependencies):  # type: ignore
    """Initialize the services."""
    initialized_services = {}
    for name, service_class in service_classes.items():
        init_parameters = list(inspect.signature(service_class.__init__).parameters)
        service_class_dependencies = {name: dep for name, dep in dependencies.items() if name in init_parameters}
        initialized_services[name] = service_class(output_port=output_ports[name], **service_class_dependencies)
    return initialized_services
