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

PARAM_REQUEST_TIMEOUT = 1.0
PARAM_REQUESTS_PER_CYCLE = 1
NODE_ONLINE_TIMEOUT = 2.0

@dataclass(slots=True)
class ParamSync:
    """Transport/request bookkeeping for a parameter."""
    setters: List[Callable[[str], None]] = field(default_factory=list)
    response_time: float = 0.0
    request_time: float = 0.0
    attempts_left: int = 5

@dataclass(slots=True)
class Param:
    value: ParamValue = None
    default_value: ParamValue = None
    min_value: ParamValue = None
    max_value: ParamValue = None
    sync: ParamSync = field(default_factory=ParamSync)

@dataclass
class FieldSync:
    value: Any = None
    setters: List[Callable[[Any], None]] = field(default_factory=list)

@dataclass
class NodeInfo:
    fields: dict = field(default_factory=dict)
    fetched: bool = False
    request_time: float = 0.0
    attempts_left: int = 5

    def bind(self, info_field, callback):
        if info_field not in self.fields:
            self.fields[info_field] = FieldSync(value=None, setters=[callback])
        else:
            self.fields[info_field].setters.append(callback)
            callback(self.fields[info_field].value)

    def update(self, fields: dict):
        self.fetched = True

        for info_field in fields:
            if info_field in self.fields:
                self.fields[info_field].value = fields[info_field]
            else:
                self.fields[info_field] = FieldSync(value=fields[info_field], setters=[])

        logger.info("NodeInfo: update(%s %s)",
                    self.fields["node_id"].value,
                    self.fields["name"].value)

        for info_field, param in self.fields.items():
            for callback in param.setters:
                callback(param.value)

@dataclass
class Node:
    nodestatus_time: float = 0.0
    uptime: float = 0.0
    boot_time: float = 0.0
    params: Dict[str, Param] = field(default_factory=dict)
    info: NodeInfo = field(default_factory=NodeInfo)
    save_required_callback: Optional[Callable] = None


@dataclass
class Publisher:
    msg: Any
    frequency: float
    timestamp: float = time.time()
    fields: dict = field(default_factory=dict)


class NodesRegistry:
    """
    Central registry of UAV nodes discovered via DroneCAN/Cyphal/ROS2 backends.

    Responsibilities:
      - Maintain per-node info, parameters, and uptime tracking.
      - Manage periodic parameter/info requests and retries.
      - Provide subscription API for frontend/UI components.
      - Abstract away backend-specific communication via callbacks.
    """
    def __init__(self,
                 request_param_get: Callable[[int, str], None],
                 request_get_info: Callable[[int, str], None]):
        self._nodes: Dict[int, Node] = {}
        self.request_param_get = request_param_get
        self.request_get_info = request_get_info

    def online_id_set(self, now=None) -> set[int]:
        """Return IDs of nodes considered online at 'now'."""
        if now is None:
            now = time.time()

        return {nid for nid, node in self._nodes.items() if self.is_online(node, now)}

    def get_node(self, node_id: int) -> Optional[Node]:
        if node_id not in self._nodes:
            return None
        return self._nodes[node_id]

    def ensure_node(self, node_id: int) -> Node:
        if node_id not in self._nodes:
            self._nodes[node_id] = Node()
        return self._nodes[node_id]

    def handle_heartbeat(self, heartbeat: dict, now=None):
        """
        This function should be called on each received Heartbeat message
        It monitors overall nodes statuses.
        """
        if now is None:
            now = time.time()

        node = self.ensure_node(heartbeat["node_id"])
        if node.nodestatus_time == 0.0:
            logger.info("Registry: node %d is online", heartbeat["node_id"])
        node.nodestatus_time = now
        node.uptime = heartbeat["uptime"]
        node.boot_time = max(node.boot_time, node.nodestatus_time - heartbeat["uptime"])

    def ensure_param(self, node_id: int, param_name: str) -> Param:
        node = self.ensure_node(node_id)
        if param_name not in node.params:
            node.params[param_name] = Param()
        return node.params[param_name]

    def subscribe_param(self, node_id: int, param_name: str, callback: Callable) -> None:
        param = self.ensure_param(node_id, param_name)
        param.sync.setters.append(callback)

    def spin(self, now=None) -> None:
        self._spin_param_requests(now)
        self._spin_node_info_requests(now)

    @staticmethod
    def is_online(node: Node, now=None) -> bool:
        if now is None:
            now = time.time()
        return node.nodestatus_time + NODE_ONLINE_TIMEOUT >= now

    def _spin_param_requests(self, now=None) -> None:
        """
        Iterate over all nodes and decide which parameters should be
        re-requested. The backend must have registered request_param_get.
        """
        if now is None:
            now = time.time()

        requests_per_this_cycle_left = 1
        for node_id, node in self._nodes.items():
            # handle params
            for param_name, param in node.params.items():
                if not NodesRegistry.is_online(node, now):
                    param.sync.attempts_left = 5
                    continue
                if param.sync.response_time > node.boot_time:
                    param.sync.attempts_left = 5
                    continue
                if param.sync.request_time + PARAM_REQUEST_TIMEOUT >= now:
                    continue
                if not param.sync.attempts_left:
                    continue

                param.sync.request_time = now
                param.sync.attempts_left -= 1
                self.request_param_get(node_id, param_name)
                requests_per_this_cycle_left -= 1
                if requests_per_this_cycle_left <= 0:
                    break

    def _spin_node_info_requests(self, now=None) -> None:
        if now is None:
            now = time.time()

        requests_per_this_cycle_left = PARAM_REQUESTS_PER_CYCLE
        for node_id, node in self._nodes.items():
            if node.info.fetched:
                continue

            recently_requested = node.info.request_time + PARAM_REQUEST_TIMEOUT >= now
            if recently_requested or not NodesRegistry.is_online(node, now):
                continue

            node = self.ensure_node(node_id)
            if node.info.attempts_left <= 0:
                return

            node.info.request_time = time.time()
            node.info.attempts_left -= 1
            logger.info("Registry: Request GetInfo node_id=%s (attempts_left=%s)",
                        node_id,
                        node.info.attempts_left)
            self.request_get_info(node_id)

            requests_per_this_cycle_left -= 1
            if requests_per_this_cycle_left <= 0:
                return

    def __iter__(self):
        return iter(self._nodes.items())
