#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>

from abc import abstractmethod
import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout

logger = logging.getLogger("base_widget")


class BaseWidget(QWidget):
    """Abstract base class for all widgets."""

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = cfg
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.init_ui()

    @abstractmethod
    def init_ui(self):
        """Initialize widget UI."""
        raise NotImplementedError

    def update_data(self, data):
        """Optional: Update widget data (e.g., sensor readings)."""
        pass

    @staticmethod
    def _apply_value_transforms(value, field_type=None, multiplier=None, offset=None):
        """Apply optional multiplier, offset, and type conversion to a value."""
        try:
            # Apply linear transform first
            if multiplier is not None:
                value = value * multiplier
            if offset is not None:
                value = value + offset

            # Apply explicit type conversion
            if field_type:
                if field_type == "int":
                    value = int(value)
                elif field_type == "float":
                    value = float(value)
                elif field_type == "bool":
                    value = bool(value)
                else:
                    logger.warning(f"Unsupported field_type: {field_type}")
        except Exception as e:
            logger.error(f"Value transform failed ({field_type}, {multiplier}, {offset}): {e}")
        return value
