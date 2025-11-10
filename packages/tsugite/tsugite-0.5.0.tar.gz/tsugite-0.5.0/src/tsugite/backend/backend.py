#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>
"""
Base Backend
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Union

logger = logging.getLogger(__name__)

# Type aliases
ParamValue = Optional[Union[bool, int, float, str]]
NodeId = Optional[int]

from tsugite.backend.registry import NodesRegistry

class BackendInitializationError(Exception):
    """Raised when a backend cannot be initialized (e.g., missing device or driver)."""
    pass

class BaseBackend(ABC):
    """Abstract base class defining the backend communication interface."""

    def __init__(self, name) -> None:
        """Initialize the base backend."""
        self.registry = None
        self.name = name
        logger.info("Hello from %sBackend", name)

    @abstractmethod
    def tick(self, dt: float) -> None:
        """Perform backend-specific periodic tasks."""

    #
    # Topics API
    #
    @abstractmethod
    def subscribe(self,
                  dtype: str,
                  cb: Callable[[str, Any], None],
                  port_name: Optional[int | str] = None,
                  node_id: Optional[int] = None) -> None:
        """Subscribe to messages from a given data type and port id."""
        logger.warning("Not implemented in %s: subscribe(%s, cb, %s, %s)",
                       self.__class__.__name__, dtype, port_name, node_id)

    @abstractmethod
    def advertise(self, topic: str, field: str, frequency: float = 10.0) -> None:
        """Register a periodic message publisher."""
        logger.warning("Not implemented in %s: advertise(%s, %s, %s)",
                       self.__class__.__name__, topic, field, frequency)

    @abstractmethod
    def set_publisher_field(self, dtype: str, field: str, value: Any) -> None:
        """Update value for an existing publisher."""
        logger.warning("Not implemented in %s: set_publisher_field(%s, %s, %s)",
                       self.__class__.__name__, dtype, field, value)

    #
    # Parameters API: read and write
    #
    def subscribe_param(self, node_id: int, param_name: str, setText: Callable) -> None:
        if self.registry is not None:
            self.registry.subscribe_param(node_id, param_name, setText)

    @abstractmethod
    def request_param_set(self, node_id: NodeId, param_name: str, value: Any) -> None:
        """
        Non-blocking request to set a parameter value.
        """
        logger.warning("Not implemented in %s: request_param_set(%s, %s, %s)",
                       self.__class__.__name__, node_id, param_name, value)

    #
    # GetInfo API
    #
    @abstractmethod
    def subscribe_get_info(self, node_id: int, field: str, callback: Callable) -> None:
        """Write a parameter value to the node."""
        logger.warning("Not implemented in %s: subscribe_get_info(%s, %s, cb)",
                       self.__class__.__name__, node_id, field)

    #
    # Commands API
    #
    def execute_command(self, node_id: int, command: str) -> None:
        """Execute command"""
        logger.warning("Not implemented in %s: execute_command(%s, %s)",
                       self.__class__.__name__, node_id, command)

def instanciate_backend(backend: str, iface: str, node_id: Optional[int]) -> BaseBackend:
    logger.info("Start backend: %s / id=%s / iface=%s", backend, node_id, iface)

    if backend == "dummy":
        from tsugite.backend.dummy_backend import DummyBackend
        communicator = DummyBackend()

    elif backend == "dronecan":
        # Supress dronecan internal logging
        logging.getLogger("dronecan").setLevel(logging.WARNING)
        from tsugite.backend.dronecan_backend import DronecanBackend
        communicator = DronecanBackend(iface=iface, node_id=node_id)

    elif backend == "cyphal":
        from tsugite.backend.cyphal_backend import CyphalBackend
        communicator = CyphalBackend()

    else:
        raise BackendInitializationError("Unknown backend")

    return communicator
