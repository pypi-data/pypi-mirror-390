#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>

import time
import logging
from typing import Dict, List, Callable, Optional, Union, Any
from dataclasses import dataclass, field

NodeId = Optional[int]
ParamValue = Optional[Union[bool, int, float, str]]

logger = logging.getLogger("registry")

@dataclass
class Param:
    value: ParamValue = None
    default_value: ParamValue = None
    min_value: ParamValue = None
    max_value: ParamValue = None
    setters: List[Callable] = field(default_factory=list)
    getset_response_time: float = 0.0
    getset_request_time: float = 0.0
    request_attempts_left: int = 5
    not_exist: Optional[bool] = None


@dataclass
class Node:
    nodestatus_time: float = 0.0
    uptime: float = 0.0
    boot_time: float = 0.0
    params: Dict[str, Param] = field(default_factory=dict)
    info: Dict[str, dict] = field(default_factory=lambda: {
        "fields": {},
        "fetched": False,
        "request_time": 0
    })
    save_required_callback: Optional[Callable] = None


@dataclass
class Publisher:
    msg: Any
    frequency: float
    timestamp: float = time.time()
    fields: dict = field(default_factory=dict)


class NodesRegistry:
    def __init__(self):
        self._nodes: Dict[int, Node] = {}

    def register_request_param_callback(self, fn: Callable[[int, str], None]) -> None:
        """
        Called by backend (DroneCAN/Cyphal) to provide the function that
        actually performs a parameter request:
            fn(node_id: int, param_name: str)
        """
        self._request_param_fn = fn

    def get_node(self, node_id: int) -> Optional[Node]:
        if node_id not in self._nodes:
            return None
        return self._nodes[node_id]

    def ensure_node(self, node_id: int) -> Node:
        if node_id not in self._nodes:
            self._nodes[node_id] = Node()
        return self._nodes[node_id]

    def handle_heartbeat(self, node_id: int, uptime: float, health: int = 0, mode: int = 0, now=time.time()):
        """
        This function should be called on each received Heartbeat message
        It monitors overall nodes statuses.
        """
        node = self.ensure_node(node_id)
        if node.nodestatus_time == 0.0:
            logger.info("Registry: node %d is online", node_id)
        node.nodestatus_time = now
        node.uptime = uptime
        node.boot_time = max(node.boot_time, node.nodestatus_time - uptime)

    def ensure_param(self, node_id: int, param_name: str) -> Param:
        node = self.ensure_node(node_id)
        if param_name not in node.params:
            node.params[param_name] = Param()
        return node.params[param_name]

    def subscribe_param(self, node_id: int, param_name: str, setText: Callable) -> None:
        param = self.ensure_param(node_id, param_name)
        param.setters.append(setText)

    def spin_param_requests(self, max_per_cycle: int = 1, min_interval: float = 1.0, now = time.time()) -> None:
        """
        Iterate over all nodes and decide which parameters should be
        re-requested. The backend must have registered _request_param_fn.
        """
        if not hasattr(self, "_request_param_fn"):
            logger.warning("No parameter request callback registered.")
            return

        left = max_per_cycle
        for node_id, node in self:
            for param_name, param in node.params.items():
                # Skip offline nodes
                if not self.is_online(node, now):
                    param.request_attempts_left = 5
                    continue

                # Reset attempts after reboot or no response for long time
                if param.getset_response_time > node.boot_time:
                    param.request_attempts_left = 5
                    continue

                # Rate limiting
                if param.getset_request_time + min_interval >= now:
                    param.request_attempts_left = 5
                    continue

                # No attempts left → give up
                if not param.request_attempts_left:
                    continue

                # Schedule one request
                param.getset_request_time = now
                param.request_attempts_left -= 1
                self._request_param_fn(node_id, param_name)
                left -= 1
                if left <= 0:
                    return

    @staticmethod
    def is_online(node: Node, now=time.time()) -> bool:
        return node.nodestatus_time + 2.0 >= now

    def __iter__(self):
        return iter(self._nodes.items())
