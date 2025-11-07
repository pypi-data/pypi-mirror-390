#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>
"""
Tsugite - A system-oriented dashboard for Cyphal (CAN + UDP) & DroneCAN (from YAML)
that renders live panels from a YAML manifest—so you watch the system, not just the bus.
"""

import os
from pathlib import Path
import argparse
import tsugite.ui.desktop.pyside_window as pyside_window

def run_with_args():
    parser = argparse.ArgumentParser(description=__doc__)

    default_config = Path("configs/examples/example.yaml")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(default_config),
        help=f"Path to YAML configuration file (default: {default_config})",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="dronecan",
        help="Communicator backend to use: dronecan|cyphal|dummy (default: dronecan)",
    )

    default_iface = "slcan:COM3@1000000" if os.name == "nt" else "slcan:/dev/ttyACM0"
    parser.add_argument(
        "--iface",
        type=str,
        default=default_iface,
        help=f"(default: {default_iface})",
    )
    parser.add_argument(
        "--node-id",
        type=int,
        default=100,
        help="(default: 100)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()

    pyside_window.main(args)

if __name__ == "__main__":
    run_with_args()
