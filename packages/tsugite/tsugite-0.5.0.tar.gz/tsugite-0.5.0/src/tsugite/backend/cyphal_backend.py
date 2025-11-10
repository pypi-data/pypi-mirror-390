#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2024 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>
"""
Cyphal backend
"""

import sys
import time
import asyncio
import logging
import threading
from typing import Callable, Any, Optional

from tsugite.backend.backend import BaseBackend, BackendInitializationError
from tsugite.backend.registry import NodesRegistry, Publisher, NodeId, ParamValue
from tsugite.utils import make_field_setter, data_type_name_to_obj

logger = logging.getLogger("cyphal_backend")

try:
    import pycyphal
    import pycyphal.application
    import uavcan.node
    import uavcan.node.Heartbeat_1_0
    import uavcan.register
    import uavcan.primitive.array
except ModuleNotFoundError:
    logger.critical("Cyphal backend requires 'pycyphal' package: pip install pycyphal")
    sys.exit(1)

class CyphalBackend(BaseBackend):
    def __init__(self) -> None:
        super().__init__(name="Cyphal")
        self.registry = NodesRegistry(self.request_param_get, self._request_get_info)
        self._running = True
        self._loop_ready = threading.Event()
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        self.node = None

        # Wait for event loop to start
        self._loop_ready.wait(timeout=5)

    #
    # Topics API
    #
    def subscribe(self,
                  dtype: str,
                  cb: Callable[[str, Any], None],
                  port_name: Optional[int | str] = None,
                  node_id: Optional[int] = None) -> None:
        """
        Public sync API — schedules async subscription inside loop.
        """
        if not dtype.startswith("cyphal."):
            logger.debug("Skipping '%s' (not Cyphal topic)", dtype)
            return None
        logger.info(f"Add Cyphal subscription: {dtype} node_id={node_id}")

        asyncio.run_coroutine_threadsafe(
            self._subscribe_async(dtype=dtype[7:], callback=cb, port_name=port_name, node_id=node_id),
            self._loop
        )

    def advertise(self, dtype: str, field: str, frequency: float = 10.0) -> None:
        if not dtype.startswith("cyphal."):
            logger.debug("Skipping '%s' (not Cyphal topic)", dtype)
            return None

        super().advertise(dtype, field, frequency)

    def set_publisher_field(self, dtype: str, field: str, value) -> None:
        if not dtype.startswith("cyphal."):
            logger.debug("Skipping '%s' (not Cyphal topic)", dtype)
            return None

        super().set_publisher_field(dtype, field, value)

    #
    # Parameters API: read and write
    #
    def request_param_set(self, node_id: NodeId, param_name: str, value: Any) -> None:
        """Write a Cyphal register (parameter) via Access_1_0."""
        if not hasattr(self, "_loop"):
            logger.error("Cyphal loop not initialized yet.")
            return None

        fut = asyncio.run_coroutine_threadsafe(
            self._register_access_async(node_id, param_name, value),
            self._loop
        )
        fut.result(timeout=0.5)  # wait for async result

    def request_param_get(self, node_id: int, param_name: str) -> None:
        """Schedule async read of a Cyphal register."""
        if not hasattr(self, "_loop"):
            logger.error("Cyphal loop not initialized yet.")
            return

        fut = asyncio.run_coroutine_threadsafe(
            self._register_access_async(node_id, param_name, None),
            self._loop
        )
        fut.result(timeout=0.5)  # wait for async result

    #
    # GetInfo API
    #
    def subscribe_get_info(self, node_id: int, field: str, callback: Callable) -> None:
        self.registry.ensure_node(node_id).info.bind(field, callback)

    #
    # Commands API
    #
    def execute_command(self, node_id: int, command: str) -> None:
        super().execute_command(node_id, command)

    def register_action(self, node_id: int, action, callback) -> None:
        pass

    def tick(self, dt: float):
        self.registry.spin()

    def _request_get_info(self, node_id: int) -> None:
        """Schedule a GetInfo request to the given Cyphal node."""
        if not hasattr(self, "_loop"):
            logger.error("Cyphal loop not initialized yet.")
            return

        asyncio.run_coroutine_threadsafe(
            self._request_get_info_async(node_id),
            self._loop
        )

    async def _request_get_info_async(self, node_id: int, attempts: int = 3) -> None:
        """Async GetInfo RPC for Cyphal."""
        try:
            import uavcan.node
        except ImportError:
            logger.error("Missing uavcan.node definitions.")
            return

        request = uavcan.node.GetInfo_1_0.Request()
        client = self.node.make_client(uavcan.node.GetInfo_1_0, node_id)

        response = None
        for attempt in range(attempts):
            if attempt == 0:
                logger.debug(f"NodeInfo: send request to {node_id}")
            else:
                logger.debug(f"NodeInfo: send request to {node_id} (attempt {attempt + 1})")

            try:
                response = await client.call(request)
            except Exception as e:
                logger.warning(f"GetInfo call error (node {node_id}): {e}")
                response = None

            if response is not None:
                break
            await asyncio.sleep(0.5)

        client.close()

        if response is None:
            logger.warning(f"Node {node_id} did not respond to GetInfo.")
            return

        # --- Parse response ---
        transfer, transfer_from = response
        rsp = transfer

        fetched_info = {
            "name": ''.join(map(chr, rsp.name)).rstrip('\x00'),
            "node_id": node_id,
            "software_version": f"v{rsp.software_version.major}.{rsp.software_version.minor}-"
                                f"{hex(rsp.software_vcs_revision_id)[2:]}",
            "hardware_version": f"v{rsp.hardware_version.major}.{rsp.hardware_version.minor}",
            "unique_id": ''.join(f"{b:02X}" for b in bytes(rsp.unique_id))
        }

        self.registry.ensure_node(node_id).info.update(fetched_info)

    @staticmethod
    def create_uavcan_register_value(value: Any) -> uavcan.register.Value_1_0:
        # Activate the right union variant
        if value is None:
            return None
        if isinstance(value, int):
            return uavcan.register.Value_1_0(natural16=uavcan.primitive.array.Natural16_1_0(value))

        logger.error(f"Unsupported param value: {value} ({type(value)})")
        return None

    async def _register_access_async(self, node_id: int, param_name: str, set_value: Any) -> None:
        """Async write parameter using uavcan.register.Access_1_0."""
        RPC_NAME = "uavcan.register.Access_1_0"
        client = self.node.make_client(uavcan.register.Access_1_0, node_id)
        request = uavcan.register.Access_1_0.Request(
            name=uavcan.register.Name_1_0(param_name),
            value=self.create_uavcan_register_value(set_value)
        )

        try:
            response, _ = await client.call(request)
        except Exception as e:
            logger.warning("%s: %s@%s - error %s", RPC_NAME, param_name, node_id, e)
            return
        finally:
            client.close()

        if response is None:
            logger.warning("%s: %s@%s - no response.", RPC_NAME, param_name, node_id)
            return

        read_value = self._decode_register_value(response.value)
        node = self.registry.get_node(node_id)
        param = node.params[param_name]
        param.sync.response_time = time.time()

        # Thread-safe update of GUI callbacks!!!
        try:
            for setText in param.sync.setters:
                setText(str(read_value))
        except Exception as e:
            logger.error("%s: %s@%s: setter callback failed: %s", RPC_NAME, param_name, node_id, e)

        if set_value is not None:
            if set_value == read_value:
                logger.info("%s: %s@%s:=%s (confirmed)", RPC_NAME, param_name, node_id, read_value)
            else:
                logger.warning("%s: %s@%s:=%s (but requested %s)", RPC_NAME, param_name, node_id, read_value, set_value)
        else:
            logger.info("%s: %s@%s:=%s (read)", RPC_NAME, param_name, node_id, read_value)

    def _run_event_loop(self):
        """Run asyncio loop in a background thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.create_task(self._main())
        self._loop_ready.set()
        try:
            self._loop.run_forever()
        except Exception as e:
            logger.exception("Event loop stopped: %s", e)
        finally:
            self._loop.close()

    async def _main(self):
        node_info = uavcan.node.GetInfo_1_0.Response(
            uavcan.node.Version_1_0(major=1, minor=0),
            name="io.github.ponomarevda.tsugite"
        )
        self.node = pycyphal.application.make_node(node_info)
        self.node.heartbeat_publisher.mode = uavcan.node.Mode_1_0.OPERATIONAL
        self.node.start()

        self.subscribe(dtype="cyphal.uavcan.node.Heartbeat_1_0", cb=self._on_heartbeat)

        while self._running:
            await asyncio.sleep(1.0)

    async def _subscribe_async(self,
                               dtype: str,
                               callback: Callable[[str, Any], None],
                               port_name: Optional[int | str] = "",
                               node_id: Optional[int] = None) -> None:
        """Internal async implementation for subscribing to Cyphal topics."""
        data_type = data_type_name_to_obj(dtype)
        if not data_type:
            logger.error("Unknown data type: %s", dtype)
            return

        # Just in case
        if port_name is None:
            port_name = ""

        sub = self.node.make_subscriber(dtype=data_type, port_name=port_name)

        def cb(msg: Any, transfer: pycyphal.transport.TransferFrom) -> None:
            if node_id is None or node_id == transfer.source_node_id:
                callback(transfer, msg)

        sub.receive_in_background(cb)

    def _on_heartbeat(self, transfer: pycyphal.transport.TransferFrom, msg: uavcan.node.Heartbeat_1_0) -> None:
        heartbeat = {
            "node_id": transfer.source_node_id,
            "uptime": msg.uptime,
            "health": msg.health,
            "mode": msg.mode
        }
        self.registry.handle_heartbeat(heartbeat)

    @staticmethod
    def _decode_register_value(value: Any) -> ParamValue:
        """
        Convert uavcan.register.Value_1_0 into a native Python type.
        Supports scalar arrays and string values.
        """
        if value is None:
            return None

        try:
            import uavcan.register
            import uavcan.primitive.array
        except ImportError:
            logger.error("Missing uavcan.register definitions.")
            return None

        # Each field in Value_1_0 is a union — only one is active at a time
        if value.natural8 is not None and len(value.natural8.value):
            return int(value.natural8.value[0])
        if value.natural16 is not None and len(value.natural16.value):
            return int(value.natural16.value[0])
        if value.integer64 is not None and len(value.integer64.value):
            return int(value.integer64.value[0])
        if value.real32 is not None and len(value.real32.value):
            return float(value.real32.value[0])
        if value.real64 is not None and len(value.real64.value):
            return float(value.real64.value[0])
        if value.boolean is not None and len(value.boolean.value):
            return bool(value.boolean.value[0])
        if value.string is not None:
            try:
                return bytes(value.string.value).decode("utf-8").rstrip("\x00")
            except Exception:
                return str(value.string.value)
        if value.natural32 is not None and len(value.natural32.value):
            return int(value.natural32.value[0])
        if value.natural64 is not None and len(value.natural64.value):
            return int(value.natural64.value[0])
        if value.integer32 is not None and len(value.integer32.value):
            return int(value.integer32.value[0])
        if value.real16 is not None and len(value.real16.value):
            return float(value.real16.value[0])

        # Default fallback: return empty or first array element if present
        for field_name in dir(value):
            field = getattr(value, field_name)
            if hasattr(field, "value") and len(field.value):
                return field.value[0]
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    a = CyphalBackend()
    for _ in range(10):
        time.sleep(10)
