#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>
"""
DroneCAN node
"""

# Pylint notes:
# - dronecan exposes members dynamically (generated DSDL), which confuses static analysis.
# pylint: disable=no-member


import os
import re
import sys
import time
import logging
import argparse
from typing import Any, Callable, Optional

from tsugite.backend.backend import BaseBackend, BackendInitializationError
from tsugite.backend.registry import NodesRegistry, Publisher, NodeId, ParamValue
from tsugite.utils import make_field_setter, data_type_name_to_obj

logger = logging.getLogger("dronecan_backend")

try:
    import serial
except ModuleNotFoundError:
    logger.critical("DroneCAN required: pip install pyserial")
    sys.exit(1)

try:
    import warnings
    # Silence DroneCAN’s internal deprecation warning
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API")
    import dronecan
except ModuleNotFoundError:
    logger.critical("DroneCAN required: pip install pydronecan setuptools==80.9.0")
    sys.exit(1)


BLINK_DURATION = 15
WRITE_ATTEMPTS = 3


class DronecanBackend(BaseBackend):
    def __init__(self, iface: str = "slcan:/dev/ttyACM0", node_id: NodeId = 100) -> None:
        super().__init__(name="Dronecan")
        self.registry = NodesRegistry(self.request_param_get, self._request_get_info)
        try:
            self.node = dronecan.make_node(
                iface, node_id=node_id, bitrate=1_000_000, baudrate=1_000_000
            )
            self.node.mode = dronecan.uavcan.protocol.NodeStatus().MODE_OPERATIONAL
            self.node.health = dronecan.uavcan.protocol.NodeStatus().HEALTH_OK
        except serial.SerialException as e:
            raise BackendInitializationError(f"Failed to open interface {iface}: {e}") from e

        self.pubs = {}
        self.node.add_handler(dronecan.uavcan.protocol.NodeStatus, self._on_heartbeat)

        #Todo: Get rid of it
        self._param_value: ParamValue = None

    #
    # Topics API
    #
    def subscribe(self,
                  dtype: str,
                  cb: Callable[[str, Any], None],
                  port_name: Optional[int | str] = None,
                  node_id: Optional[int] = None) -> None:
        if not dtype.startswith("dronecan."):
            logger.debug("Skipping '%s' (not DroneCAN topic)", dtype)
            return None

        data_type = data_type_name_to_obj(dtype)
        if not data_type:
            return

        def _handler(msg) -> None:
            if node_id is None or msg.transfer.source_node_id == node_id:
                cb(data_type, msg.message)

        self.node.add_handler(data_type, _handler)

    def advertise(self, dtype: str, field: str, frequency: float = 1.0) -> None:
        if not dtype.startswith("dronecan."):
            logger.debug("Skipping '%s' (not DroneCAN topic)", dtype)
            return None

        data_type = data_type_name_to_obj(dtype)
        if not data_type:
            return

        if not isinstance(field, str):
            raise ValueError("Field must be a string")

        if dtype not in self.pubs:
            self.pubs[dtype] = Publisher(msg=data_type(), frequency=frequency)
            logger.info("Add publisher: %s", dtype)

            # Apply hacks for some topics
            if dtype == "dronecan.uavcan.equipment.esc.RawCommand":
                self.pubs[dtype].msg.cmd = [int(0)] * 8
            elif dtype == "dronecan.uavcan.equipment.actuator.ArrayCommand":
                for _ in range(4):
                    self.pubs[dtype].msg.commands.append(self.pubs[dtype].msg.commands.new_item())
        else:
            self.pubs[dtype] = self.pubs[dtype]

        self.pubs[dtype].fields[field] = make_field_setter(self.pubs[dtype].msg, field)
        logger.info("Add publisher field setter: %s.%s", dtype, field)

    def set_publisher_field(self, dtype: str, field: str, value: Any) -> None:
        if dtype not in self.pubs:
            logger.warning("Topic '%s' not registered for periodic publishing", dtype)
            return

        if field not in self.pubs[dtype].fields:
            logger.warning("Field '%s' not registered for topic '%s'", field, dtype)
            return

        self.pubs[dtype].fields[field](value)

    #
    # Parameters API: read and write
    #
    def request_param_set(self, node_id: NodeId, param_name: str, value: Any) -> None:
        if not isinstance(node_id, int) or node_id < 1 or node_id > 0x7F:
            logger.warning("Write param: failed because the node ID is incorrect: %s", node_id)
            return

        req = dronecan.uavcan.protocol.param.GetSet.Request()
        req.name = param_name

        if isinstance(value, int):
            req.value.integer_value = value
        elif isinstance(value, str):
            encoded = value.encode("utf-8")
            req.value.string_value = list(encoded)
            if len(req.value.string_value) == 0:
                req.value.string_value = [255]

        self.node.request(req, node_id, lambda x: self._getset_callback(x, "Write"))

        node = self.registry.ensure_node(node_id)
        if node.save_required_callback:
            node.save_required_callback(BLINK_DURATION)

        logger.info("Write param: node %s %s=%s", node_id, param_name, value)

    def request_param_get(self, node_id: int, param_name: str) -> None:
        if not isinstance(node_id, int):
            raise ValueError(f"node_id {node_id} is not int")
        if not isinstance(param_name, str):
            raise ValueError(f"param_name {param_name} is not str")

        req = dronecan.uavcan.protocol.param.GetSet.Request()
        req.name = param_name
        self.node.request(req, node_id, lambda x: self._getset_callback(x, "Read"))

    #
    # GetInfo API
    #
    def subscribe_get_info(self, node_id: int, field: str, callback: Callable[[str, Any], None]) -> None:
        self.registry.ensure_node(node_id).info.bind(field, callback)

    #
    # Commands API
    #
    def execute_command(self, node_id: int, command: str) -> None:
        commands = {
            "reboot":   self._execute_reboot,
            "save_all": self._execute_save_all,
            "upgrade":  self._execute_upgrade,
        }

        if command not in commands:
            logger.warning("Execute command: %s not supported.", command)
            return

        commands[command](node_id)

    def register_action(self, node_id: int, action, callback):
        if action == "save_all":
            node = self.registry.ensure_node(node_id)
            node.save_required_callback = callback

    def tick(self, dt: float) -> None:
        try:
            self.node.spin(0.01)
        except KeyboardInterrupt:
            logger.info("Terminated by user.")
            sys.exit(0)
        except NotImplementedError:
            logger.critical("NotImplementedError. Check python-can == 4.3 is installed.")
            sys.exit(1)
        except dronecan.transport.TransferError:
            pass
        except dronecan.driver.common.DriverError:
            logger.critical("dronecan.driver.common.DriverError")
            sys.exit(1)
        except ValueError as e:
            logger.error("ValueError: %s", e)
        except dronecan.driver.common.TxQueueFullError as e:
            logger.error("TxQueueFullError: %s", e)
        except serial.serialutil.SerialException as e:
            logger.critical("SerialException: %s", e)
            sys.exit(1)

        # periodic publishers
        for _, pub in self.pubs.items():
            current_time = time.time()
            if current_time - pub.timestamp >= 1 / pub.frequency:
                try:
                    self.node.broadcast(pub.msg)
                except dronecan.driver.common.TxQueueFullError as e:
                    logger.critical("TxQueueFullError: %s", e)
                    sys.exit(1)
                pub.timestamp = current_time

        # handle params and info refresh
        self.registry.spin()

    @staticmethod
    def _decode_uavcan_protocol_param_value(value: dronecan.transport.CompoundValue) -> ParamValue:
        if value is None:
            return None
        if hasattr(value, "boolean_value"):
            return bool(value.boolean_value)
        if hasattr(value, "integer_value"):
            return int(value.integer_value)
        if hasattr(value, "real_value"):
            return float(value.real_value)
        if hasattr(value, "string_value"):
            string = value.string_value
            return str(string) if len(string) > 0 and string[0] != 255 else ""
        return None

    def _execute_reboot(self, node_id: int):
        def _callback(msg: dronecan.uavcan.protocol.RestartNode.Response):
            if msg is None:
                return
        req = dronecan.uavcan.protocol.RestartNode.Request()
        req.magic_number = 0xACCE551B1E
        self.node.request(req, node_id, _callback)
        self.tick(0.01)
        logger.info("Execute action: reboot node %d.", node_id)

    def _execute_save_all(self, node_id: int):
        def _callback(msg: dronecan.uavcan.protocol.param.ExecuteOpcode.Response):
            if msg is None:
                return

        req = dronecan.uavcan.protocol.param.ExecuteOpcode.Request()
        req.opcode = 0    # Save all parameters to non-volatile storage
        req.argument = 0  # Reserved, keep zero
        self.node.request(req, node_id, _callback)
        self.tick(0.01)
        logger.info("Execute action: save_all node %d.", node_id)

    def _execute_upgrade(self, node_id: int):
        logger.warning("Action 'upgrade' is not supported yet.")

    def _request_get_info(self, node_id: int):
        req = dronecan.uavcan.protocol.GetNodeInfo.Request()
        self.node.request(req, node_id, self._get_info_callback)
        self.tick(0.01)

    def _on_heartbeat(self, msg: dronecan.node.TransferEvent):
        heartbeat = {
            "node_id": msg.transfer.source_node_id,
            "uptime": msg.message.uptime_sec,
            "health": msg.message.health,
            "mode": msg.message.mode
        }
        self.registry.handle_heartbeat(heartbeat)

    def _get_info_callback(self, transfer_event: dronecan.node.TransferEvent):
        if transfer_event is None:
            logger.warning("GetInfo: transfer is None")
            return

        rsp = transfer_event.response
        node_id = transfer_event.transfer.source_node_id

        fetched_info = {
            "name": rsp.name.decode("utf-8").rstrip("\x00"),
            "node_id": node_id,
            "software_version": f"v{rsp.software_version.major}.{rsp.software_version.minor}-"
                                f"{hex(rsp.software_version.vcs_commit)[2:]}",
            "hardware_version": f"v{rsp.hardware_version.major}.{rsp.hardware_version.minor}",
            "unique_id": "".join(f"{b:02X}" for b in bytes(rsp.hardware_version.unique_id))
        }

        self.registry.ensure_node(node_id).info.update(fetched_info)

    def _getset_callback(self, msg: dronecan.node.TransferEvent, operation: str):
        if not isinstance(msg, dronecan.node.TransferEvent):
            # It happens sometime
            logger.warning("%s param: msg %s is not TransferEvent", operation, msg)
            return

        node_id = msg.transfer.source_node_id

        node = self.registry.get_node(node_id)
        if not node:
            logger.critical("%s param: not node", operation)
            return

        response_name = msg.response.name.decode("utf-8").rstrip("\x00")
        if len(response_name) == 0:
            logger.warning("%s param: node %s doesn't have the requested param", operation, node_id)
            # Unfortunatelly, the response doesn't say which exactly parameter doesn't exist!
            # Better to make responses with the name and empty value in such cases!
            return

        if response_name not in node.params:
            # It happens sometime
            logger.critical("%s param: response_name not in node.params", operation)
            return

        param = node.params[response_name]
        param.sync.response_time = time.time()
        param.value = DronecanBackend._decode_uavcan_protocol_param_value(msg.response.value)
        param.default_value = DronecanBackend._decode_uavcan_protocol_param_value(msg.response.default_value)
        param.max_value = DronecanBackend._decode_uavcan_protocol_param_value(msg.response.max_value)
        param.min_value = DronecanBackend._decode_uavcan_protocol_param_value(msg.response.min_value)

        for setText in param.sync.setters:
            setText(str(param.value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    default_iface = "slcan:COM3@1000000" if os.name == "nt" else "slcan:/dev/ttyACM0"
    parser.add_argument("-i", "--iface", type=str, default=default_iface,
                        help="CAN interface, e.g. 'socketcan:can0' or 'slcan:/dev/ttyACM0@1000000'")
    parser.add_argument("-n", "--node-id", type=int, default=100,
                        help="DroneCAN node ID (default: 100)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    backend = DronecanBackend(iface=args.iface, node_id=args.node_id)
    backend.subscribe(dtype="dronecan.uavcan.protocol.NodeStatus",
                      cb=lambda topic, msg: logger.info("NodeStatus: %s: %s", topic, msg))
    while True:
        backend.tick(0.01)


if __name__ == "__main__":
    main()
