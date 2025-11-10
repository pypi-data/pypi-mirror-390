#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>

import sys
import logging
import importlib
from collections import deque

from PySide6.QtCore import Qt, QTimer, QThread, QSize, QMetaObject, Q_ARG, Slot
from PySide6.QtGui import QFontMetrics, QPixmap, QColor, QPalette
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSizePolicy,
    QSlider,
)

from tsugite.utils import resolve_field_path
from tsugite.ui.desktop.base_widget import BaseWidget
from tsugite.ui.desktop.gps_widget import GpsWidget

logger = logging.getLogger(__name__)

def lazy_import_module(widget_name, module_name):
    """ Lazy imports: only load these when widget is created """
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        logger.critical(f"{widget_name} required {module_name}. You can install it: pip install {module_name}")
        sys.exit(1)

class WidgetFactory:
    """Factory for creating widgets from YAML definitions."""

    registry = {
        "const_label":  lambda cfg: ConstLabelWidget(cfg),
        "BoundLabel":   lambda cfg: BoundLabel(cfg),
        "EnumStatusLabel":  lambda cfg: EnumStatusLabel(cfg),
        "ParamWidget":  lambda cfg: ParamWidget(cfg),
        "HealthLabel":  lambda cfg: HealthLabel(cfg),
        "BoundImage":   lambda cfg: BoundImage(cfg),
        "PlotWidget" :  lambda cfg: PlotWidget(cfg),
        "GpsWidget":    lambda cfg: GpsWidget(cfg),
        "ButtonWidget": lambda cfg: ButtonWidget(cfg),
        "table":        lambda cfg: TableWidget(cfg),
        "TemplateTableWidget":      lambda cfg: TemplateTableWidget(cfg),
        "HorizontalSlider": lambda cfg: HorizontalSliderWidget(cfg),
        "DialWidget":       lambda cfg: DialWidget(cfg),
        "PublisherWidget":  lambda cfg: PublisherWidget(cfg),
        "CanGraphWidget": lambda cfg: CanGraphWidget(cfg),
    }

    @classmethod
    def create(cls, widget_cfg: dict):
        wtype = widget_cfg.get("type", "")
        if wtype in cls.registry:
            return cls.registry[wtype](widget_cfg)
        # return a valid BaseWidget (ConstLabelWidget expects a dict cfg)
        return ConstLabelWidget({"text": f"{wtype} - Unknown widget type"})

class ConstLabelWidget(BaseWidget):
    """Simple text/label widget."""

    def init_ui(self):
        # always coerce to string for QLabel ctor
        self.label = QLabel(str(self.cfg.get("text")))
        self.layout.addWidget(self.label)

    def update_data(self, data):
        if isinstance(data, str):
            self.label.setText(data)
        elif isinstance(data, dict) and "text" in data:
            self.label.setText(str(data["text"]))
        else:
            # also handle ints/floats/etc. safely
            self.label.setText(str(data))


class BoundLabel(QLabel):
    """
    A label that updates from one or more communicator topics.

    Supports:
      - Nested fields: e.g. "timestamp.usec"
      - Indexed fields: e.g. "accelerometer_integral[0]"
      - Mixed paths: e.g. "data.vector[2].x"
      - Unified topic::field form, e.g. "cyphal.uavcan.node.Heartbeat_1_0::uptime"

    YAML form:

      topics:
        - dronecan.uavcan.protocol.NodeStatus::uptime_sec
        - cyphal.uavcan.node.Heartbeat_1_0::uptime

    Optional transforms:
      multiplier: 0.001
      offset: 273.15
      field_type: float
      precision: 3
      unit: "V"
      default: "-"
    """

    def __init__(self, cfg):
        # --- default value (startup and fallback) ---
        default_text = str(cfg.get("default", cfg.get("text", "-")))
        super().__init__(default_text)
        self.default_text = default_text

        communicator = cfg.get("communicator")
        if not communicator:
            return

        self.communicator = communicator
        node_id = cfg.get("node_id", None)
        topics = cfg.get("topics")
        info = cfg.get("info")

        # --- value transform options ---
        self.multiplier = cfg.get("multiplier")
        self.offset = cfg.get("offset")
        self.field_type = cfg.get("field_type")
        self.precision = int(cfg.get("precision", 3))
        self.unit = cfg.get("unit", "")

        if info and node_id is not None:
            communicator.subscribe_get_info(node_id, info, self._on_info)
            return

        # Parse topics
        self.topic_field_pairs = []
        if topics:
            for t in topics:
                dtype, field = self._parse_topic_field(t)
                self.topic_field_pairs.append((dtype, field))

        # Subscribe
        for dtype, field in self.topic_field_pairs:
            communicator.subscribe(
                dtype=dtype,
                cb=lambda t, msg, f=field: self._on_msg(msg, f),
                node_id=node_id,
            )

    @staticmethod
    def _parse_topic_field(topic_str: str):
        """Split topic::field into (dtype, field)."""
        if "::" in topic_str:
            dtype, field = topic_str.split("::", 1)
        else:
            dtype, field = topic_str, None
        return dtype, field

    def _on_info(self, value):
        """Handle info responses (same logic as regular message)."""
        if value is None:
            self.setText(self.default_text)
        else:
            self._update_text(value)

    def _on_msg(self, msg, field):
        """Receive message and update text with optional value transform."""
        value = resolve_field_path(msg, field)
        if value is None:
            self.setText(self.default_text)
            return
        self._update_text(value)

    def _update_text(self, value):
        """Format, transform, and display the value."""
        # --- apply numeric transforms ---
        try:
            if isinstance(value, (int, float)):
                if self.multiplier is not None:
                    value = value * float(self.multiplier)
                if self.offset is not None:
                    value = value + float(self.offset)
                if self.field_type:
                    if self.field_type == "int":
                        value = int(value)
                    elif self.field_type == "float":
                        value = float(value)
                    elif self.field_type == "bool":
                        value = bool(value)
        except Exception as e:
            logger.warning(f"BoundLabel transform failed: {e}")
            self.setText(self.default_text)
            return

        # --- format output ---
        if isinstance(value, float):
            fmt = f"{{:.{self.precision}f}}"
            text = fmt.format(value)
        elif isinstance(value, (list, tuple)):
            fmt = f"{{:.{self.precision}f}}"
            text = ", ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in value)
        else:
            text = str(value)

        if self.unit:
            text = f"{text} {self.unit}"

        self.setText(text)

class EnumStatusLabel(QLabel):
    """
    Color-coded enum label for CAN/DroneCAN/Cyphal fields.

    Supports single or multiple topic/field pairs.

    YAML examples:
      # Single source
      type: EnumStatusLabel
      topic: cyphal.uavcan.node.Heartbeat_1_0
      field: health
      node_id: 10
      mapping:
        None: {text: "OFF",  color: "red"}
        0:    {text: "OK",   color: "green"}
        1:    {text: "WARN", color: "yellow"}
        2:    {text: "ERR",  color: "purple"}
        3:    {text: "CRIT", color: "red"}

      # Multi-source (DroneCAN + Cyphal)
      type: EnumStatusLabel
      topics: [dronecan.uavcan.protocol.NodeStatus, cyphal.uavcan.node.Heartbeat_1_0]
      fields: [health, health.value]
      node_id: 42
      mapping: { ...same as above... }
    """

    def __init__(self, cfg):
        super().__init__(cfg.get("text", "-"))
        self.communicator = cfg.get("communicator")
        if not self.communicator:
            return

        self.node_id = cfg.get("node_id")

        # Multi-topic/field support
        topics = cfg.get("topics")
        fields = cfg.get("fields")
        if topics and fields:
            self.topic_field_pairs = list(zip(topics, fields))
        else:
            topic = cfg.get("topic")
            field = cfg.get("field")
            self.topic_field_pairs = [(topic, field)] if topic and field else []

        # Normalize mapping keys
        raw_mapping = cfg.get("mapping", {})
        self.mapping = {}
        for k, v in raw_mapping.items():
            if k in (None, "None", "null", "NULL"):
                self.mapping[None] = v
            else:
                try:
                    self.mapping[int(k)] = v
                except (TypeError, ValueError):
                    self.mapping[k] = v

        self.offline_entry = self.mapping.get(None, {"text": "OFF", "color": "red"})

        # Initial style
        self._apply_style(self.offline_entry["text"], self.offline_entry["color"])

        # Subscribe to all topic/field pairs
        for topic, field in self.topic_field_pairs:
            self.communicator.subscribe(
                dtype=topic,
                cb=lambda t, msg, f=field: self._on_msg(msg, f),
                node_id=self.node_id,
            )

    def _on_msg(self, msg, field):
        value = resolve_field_path(msg, field)
        entry = self.mapping.get(value, self.offline_entry)
        self._apply_style(entry["text"], entry["color"])

    def _apply_style(self, text: str, color: str):
        """Force color regardless of parent styles."""
        self.setText(text)
        self.setStyleSheet(f"color: {color} !important; font-weight: bold;")

class HealthLabel(EnumStatusLabel):
    """
    Specialized EnumStatusLabel for standard UAVCAN/Cyphal node health.

    YAML example:
      type: HealthLabel
      node_id: 42
    """

    def __init__(self, cfg):
        base_cfg = dict(cfg)

        base_cfg.setdefault("topics", [
            "dronecan.uavcan.protocol.NodeStatus",
            "cyphal.uavcan.node.Heartbeat_1_0"
        ])
        base_cfg.setdefault("fields", [
            "health",
            "health.value"
        ])
        base_cfg.setdefault("mapping", {
            None: {"text": "OFF",  "color": "red"},
            0:    {"text": "OK",   "color": "green"},
            1:    {"text": "WARN", "color": "yellow"},
            2:    {"text": "ERR",  "color": "purple"},
            3:    {"text": "CRIT", "color": "red"},
        })

        super().__init__(base_cfg)

class ParamWidget(BaseWidget):
    """
    Editable parameter widget that both fetches and allows updating a parameter.

    YAML example:
      type: ParamWidget
      param: "pwm1.min"
      node_id: 51
      editable: true
      refresh: 2.0   # optional: refresh interval in seconds
    """

    def init_ui(self):
        from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit

        cfg = self.cfg
        self.param_name = cfg.get("param")
        self.node_id = int(cfg.get("node_id"))
        self.editable = bool(cfg.get("editable", True))
        self.default_value = str(cfg.get("default", ""))
        self.communicator = cfg.get("communicator")
        self.prev_text = ""

        # Layout
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(4)

        # Editable value field
        self.input = QLineEdit()
        self.input.setAlignment(Qt.AlignLeft)
        self.input.setFixedWidth(80)
        self.input.setEnabled(self.editable)
        self.input.setText(self.default_value)
        h.addWidget(self.input)

        self.layout.addLayout(h)

        # Signals for user edits
        self.input.editingFinished.connect(self._on_user_edit)

        if not self.communicator or not self.param_name or self.node_id is None:
            self.input.setText("ERR")
            return

        self.normal_palette = self.input.palette()  # save current palette

        self.communicator.subscribe_param(self.node_id, self.param_name, self.setText)

    def setText(self, text):
        """Thread-safe: may be called from any thread."""
        if QThread.currentThread() != self.thread():
            # We're in a background thread → re-invoke safely in GUI thread
            QMetaObject.invokeMethod(
                self,
                "_setText_internal",
                Qt.QueuedConnection,
                Q_ARG(str, text)
            )
            return

        # We're already in GUI thread → safe to update immediately
        self._setText_internal(text)

    @Slot(str)
    def _setText_internal(self, text):
        """Actual UI update logic (runs in GUI thread only)."""
        if text in (None, "", "offline"):
            text = self.default_value

        self.prev_text = text
        self.input.setText(text)

        # Restore normal tint with a short success flash
        self._set_field_tint(QColor("#8fce00"))  # green tint
        QTimer.singleShot(200, lambda: self._set_field_tint(None))

    def _on_user_edit(self):
        """Handle manual edit by user."""
        text = self.input.text().strip()
        if not text or not self.communicator:
            return

        if text == self.prev_text:
            return  # skip because nothing has changed

        try:
            if "." in text:
                val = float(text)
            else:
                val = int(text)
        except ValueError:
            # Not a number — treat as string
            val = text

        # Optional validation:
        if isinstance(val, str) and len(val) > 63:
            logger.warning(f"String too long for parameter {self.param_name}")
            self._set_field_tint(QColor("#ff4d4d"))  # red tint for invalid
            QTimer.singleShot(1000, lambda: self._set_field_tint(None))
            return

        # set pending tint (soft yellow)
        self._set_field_tint(QColor("#ffd966"))

        self.communicator.request_param_set(self.node_id, self.param_name, val)

    def _set_field_tint(self, color: QColor | None):
        """Apply a temporary background tint (theme-safe)."""
        pal = self.normal_palette
        if color:
            pal = QPalette(pal)
            base = pal.color(QPalette.Base)
            # Mix base with tint (70% base, 30% tint)
            mixed = QColor(
                int(base.red() * 0.7 + color.red() * 0.3),
                int(base.green() * 0.7 + color.green() * 0.3),
                int(base.blue() * 0.7 + color.blue() * 0.3),
            )
            pal.setColor(QPalette.Base, mixed)
        self.input.setPalette(pal)

    def focusInEvent(self, event):
        """Mark as user editing to prevent background refreshes."""
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Write value when leaving the field."""
        self._on_user_edit()
        super().focusOutEvent(event)


class ButtonWidget(BaseWidget):
    """
    A configurable button that performs different actions.

    YAML example:
      type: ButtonWidget
      text: "Save all parameters"
      action: noop | save_all | reboot | update_firmware
      node_id: 63
    """

    def init_ui(self):
        self.button = QPushButton(self.cfg.get("text", "Button"))
        self.layout.addWidget(self.button)

        self.action = self.cfg.get("action", "noop")
        self.node_id = self.cfg.get("node_id")
        self.communicator = self.cfg.get("communicator")

        self._blink_timer = None
        self._blink_on = False

        def execute_command_callback():
            self.communicator.execute_command(node_id=self.node_id, command=self.action)
        self.button.clicked.connect(execute_command_callback)

        if self.action == "save_all":
            self.communicator.register_action(self.node_id, self.action, self.start_hint)

    def start_hint(self, duration: float | None = None):
        """Start blinking the button to attract user's attention."""
        if self._blink_timer is not None:
            return

        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._toggle_blink)
        self._blink_timer.start(500)
        logger.debug("Blinking started for button '%s'", self.button.text())

        if duration is not None and duration > 0:
            QTimer.singleShot(int(duration * 1000), self.stop_hint)

    def stop_hint(self):
        """Stop blinking and restore the button style."""
        if self._blink_timer:
            self._blink_timer.stop()
            self._blink_timer = None
        self.button.setStyleSheet("")
        self.button.style().unpolish(self.button)
        self.button.style().polish(self.button)
        self.button.update()
        self._blink_on = False
        logger.debug("Blinking stopped for button '%s'", self.button.text())

    def _toggle_blink(self):
        """Toggle between two visual styles."""
        self._blink_on = not self._blink_on
        if self._blink_on:
            self.button.setStyleSheet("background-color: #fff4b3; color: black; font-weight: bold;")
        else:
            self.button.setStyleSheet("")

        self.button.style().unpolish(self.button)
        self.button.style().polish(self.button)
        self.button.update()

class RowWidget(QWidget):
    """Dynamic table row with flexible columns based on header definition.

    Cells may be:
      - QWidget instances (used directly)
      - dict: a widget config (must include "type"; WidgetFactory.create will be used)
      - list: a sequence of widget configs or widgets (rendered horizontally inside the cell)
      - scalar: treated as text and wrapped by ConstLabelWidget

    The optional communicator is injected into nested widget configs when present.
    """

    def __init__(self, fields: list[str], values: dict | list, widths=None, bold=False, communicator=None):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        style_suffix = "font-weight: bold;" if bold else ""
        self.fields = fields
        self.widths = widths or []
        self.communicator = communicator

        # Normalize data
        if isinstance(values, dict):
            cell_values = [values.get(key, "") for key in fields]
        else:
            cell_values = [v for v in values]

        max_height = 0
        for i, (key, cell_value) in enumerate(zip(fields, cell_values)):
            widget = None

            # If the cell is already a QWidget, use it directly
            if isinstance(cell_value, QWidget):
                widget = cell_value

            # If the cell is a dict with 'widgets' key -> composite cell
            elif isinstance(cell_value, dict) and "widgets" in cell_value and isinstance(cell_value["widgets"], list):
                container = QWidget()
                h = QHBoxLayout()
                h.setContentsMargins(0, 0, 0, 0)
                h.setSpacing(6)
                # create each inner widget
                for sub in cell_value["widgets"]:
                    sub_cfg = dict(sub) if isinstance(sub, dict) else sub
                    if isinstance(sub_cfg, dict) and self.communicator and "communicator" not in sub_cfg:
                        sub_cfg["communicator"] = self.communicator
                    sub_widget = sub_cfg if isinstance(sub_cfg, QWidget) else WidgetFactory.create(sub_cfg) if isinstance(sub_cfg, dict) else ConstLabelWidget({"text": str(sub_cfg)})
                    h.addWidget(sub_widget)
                    try:
                        hint = sub_widget.sizeHint().height()
                        if hint > max_height:
                            max_height = hint
                    except Exception as err:
                        logger.error(err)
                container.setLayout(h)
                widget = container

            # If the cell is a list -> render each element inside a container
            elif isinstance(cell_value, list):
                container = QWidget()
                h = QHBoxLayout()
                h.setContentsMargins(0, 0, 0, 0)
                h.setSpacing(6)
                for sub in cell_value:
                    if isinstance(sub, QWidget):
                        sub_widget = sub
                    elif isinstance(sub, dict):
                        sub_cfg = dict(sub)
                        if self.communicator and "communicator" not in sub_cfg:
                            sub_cfg["communicator"] = self.communicator
                        sub_widget = WidgetFactory.create(sub_cfg)
                    else:
                        sub_widget = ConstLabelWidget({"text": str(sub)})
                    h.addWidget(sub_widget)
                    try:
                        hint = sub_widget.sizeHint().height()
                        if hint > max_height:
                            max_height = hint
                    except Exception as err:
                        logger.error(err)
                container.setLayout(h)
                widget = container

            # If the cell is a dict -> treat as a single widget config
            elif isinstance(cell_value, dict):
                cfg = dict(cell_value)
                if self.communicator and "communicator" not in cfg:
                    cfg["communicator"] = self.communicator
                widget = WidgetFactory.create(cfg)

            # fallback: treat as scalar text
            else:
                widget = ConstLabelWidget({"text": str(cell_value)})

            # Apply styling (best-effort; widgets may override)
            try:
                # Skip styling for color-aware widgets
                if isinstance(widget, (EnumStatusLabel, BoundLabel, BoundImage)):
                    pass
                else:
                    color = self._text_color(key, str(cell_value), bold)
                    widget.setStyleSheet(f"color: {color}; {style_suffix} padding: 0; margin: 0;")
            except Exception as err:
                logger.error(err)

            # Apply width if requested
            if i < len(self.widths):
                try:
                    widget.setFixedWidth(self.widths[i])
                except Exception as err:
                    logger.error(err)

            layout.addWidget(widget)
            # update max height from sizeHint
            try:
                hint = widget.sizeHint().height()
                # Clamp images to a reasonable max row height
                if isinstance(widget, QLabel) and widget.pixmap() is not None:
                    hint = min(hint, 32)  # e.g. max 32 px high
                if hint > max_height:
                    max_height = hint
            except Exception as err:
                logger.error(err)

        self.setLayout(layout)
        # keep rows compact but large enough for contents
        if max_height > 0:
            self.setFixedHeight(max(20, max_height + 2))
        else:
            self.setFixedHeight(20)

    def _text_color(self, key: str, text: str, bold: bool) -> str:
        if bold:
            return "#ccc"
        s = str(text).lower()
        if key in ("status", "update"):
            if "ok" in s:
                return "#00ff88"
            elif "off" in s:
                return "#ff4444"
            elif "warn" in s:
                return "#ffaa00"
        return "white"


class TableWidget(BaseWidget):
    """Generic table widget using header dict for field mapping, with auto column width.

    Cells inside rows may be provided as widget configs (dict with 'type') or plain scalars.
    TableWidget will inject the parent/ panel communicator into nested widget configs when present.
    """

    def __init__(self, cfg: dict):
        # keep cfg/communicator for nested widgets in cells
        self.cfg = cfg
        self.communicator = cfg.get("communicator")
        self.header_dict = cfg.get("header", {})
        self.fields = list(self.header_dict.keys())
        self.header_labels = list(self.header_dict.values())
        self.rows = cfg.get("rows", [])

        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.init_ui()

    def compute_column_widths(self, font_metrics):
        """Compute max text width for each column.

        If a cell is a dict with a 'text' key, use that text. Otherwise fall back
        to string conversion. Also handle lists/composite cells by inspecting
        their first text-like element.
        """
        widths = [0] * len(self.fields)

        for i, label in enumerate(self.header_labels):
            widths[i] = max(widths[i], font_metrics.horizontalAdvance(str(label)))

        for row in self.rows:
            for i, key in enumerate(self.fields):
                val = row.get(key, "")
                text = ""
                # extract representative text if it's a widget config or composite
                if isinstance(val, dict):
                    if "text" in val:
                        text = val.get("text")
                    elif "widgets" in val and isinstance(val["widgets"], list) and val["widgets"]:
                        first = val["widgets"][0]
                        text = first.get("text", str(first)) if isinstance(first, dict) else str(first)
                    else:
                        text = val.get("label", val.get("name", ""))
                elif isinstance(val, list) and val:
                    first = val[0]
                    if isinstance(first, dict):
                        text = first.get("text", first.get("name", ""))
                    else:
                        text = str(first)
                else:
                    text = str(val)

                widths[i] = max(widths[i], font_metrics.horizontalAdvance(text))

        # small padding for cell margins
        return [w + 16 for w in widths]

    def init_ui(self):
        fm = QFontMetrics(self.font())
        col_widths = self.compute_column_widths(fm)

        if self.header_labels:
            header_row = RowWidget(self.fields, self.header_labels, widths=col_widths, bold=True, communicator=self.communicator)
            header_row.setStyleSheet("background-color: #222;")
            self.layout.addWidget(header_row)

        for row in self.rows:
            self.layout.addWidget(RowWidget(self.fields, row, widths=col_widths, communicator=self.communicator))

class TemplateTableWidget(BaseWidget):
    """
    Pattern-driven table with optional discovery via registry.online_id_set().

    Behavior:
      - Seed (hardcoded) nodes are created first in the given order and are ALWAYS visible.
      - Discovered nodes (not in seeds) are appended after seeds.
      - Discovered rows are shown only while online; when offline they are hidden.
      - Rows are never deleted.
      - Column widths are derived ONLY from header labels (like TableWidget baseline).
    """

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.communicator = cfg.get("communicator")
        self.registry = getattr(self.communicator, "registry", None)

        # --- config ---
        self.header_labels: list[str] = [str(x) for x in (cfg.get("header") or [])]
        self.pattern_list: list = list(cfg.get("pattern") or [])
        self.items: list[dict] = list(cfg.get("items") or [])
        self.discover: bool = bool(cfg.get("discover", True))

        # derive simple field keys (for RowWidget)
        self.fields = [self._to_key(lbl) for lbl in self.header_labels]

        # align pattern length with header length
        n = len(self.header_labels)
        if len(self.pattern_list) > n:
            self.pattern_list = self.pattern_list[:n]
        elif len(self.pattern_list) < n:
            self.pattern_list += [""] * (n - len(self.pattern_list))

        # seeds and friendly names (keep order as provided)
        self.seed_ids: list[int] = [it["id"] for it in self.items if "id" in it]
        self.name_by_id: dict = {it["id"]: it.get("name", f"Node {it['id']}") for it in self.items if "id" in it}

        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        # --- column widths based ONLY on headers ---
        fm = QFontMetrics(self.font())
        self.col_widths = self._header_based_widths(fm, self.header_labels)

        # header row (apply widths so columns align)
        if self.header_labels:
            header = RowWidget(self.fields, self.header_labels,
                               widths=self.col_widths, bold=True,
                               communicator=self.communicator)
            header.setStyleSheet("background-color: #222;")
            self.layout.addWidget(header)

        # container for rows; never delete, only hide/show
        self.rows_by_id: dict[int, RowWidget] = {}

        # initial rows: create ALL seeds first (keep their order)
        initial_online = self._get_discovered_ids()
        for nid in self.seed_ids:
            self._ensure_row(nid)

        # then create discovered extras (exclude seeds), sorted
        for nid in sorted(initial_online - set(self.seed_ids), key=self._sort_key):
            self._ensure_row(nid)

        # set visibility (seeds always visible; extras only if online)
        self._apply_online_visibility(initial_online)

        # polling (fixed 1s)
        self._timer = None
        if self.discover and self.registry:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._poll_discovery)
            self._timer.start(1000)

    def init_ui(self):
        pass  # all done in __init__

    # ---------- discovery / visibility ----------
    def _get_discovered_ids(self) -> set[int]:
        if self.registry and hasattr(self.registry, "online_id_set"):
            try:
                return set(self.registry.online_id_set())
            except Exception:
                return set()
        return set()

    def _poll_discovery(self):
        online = self._get_discovered_ids()

        # create rows for any newly-seen IDs that are not seeds
        for nid in sorted(online - set(self.seed_ids), key=self._sort_key):
            if nid not in self.rows_by_id:
                self._ensure_row(nid)

        # update visibility (seeds always visible; extras only while online)
        self._apply_online_visibility(online)

    def _apply_online_visibility(self, online_ids: set[int]):
        online = set(online_ids)
        seed_set = set(self.seed_ids)

        for nid, row in self.rows_by_id.items():
            if nid in seed_set:
                # seeds: mandatory, always visible
                row.setVisible(True)
            else:
                # extras: only visible while online
                row.setVisible(nid in online)

    # ---------- row creation ----------
    def _ensure_row(self, node_id: int):
        """Create row once; subsequent updates just toggle visibility."""
        if node_id in self.rows_by_id:
            return

        cells = self._filled_cells_for_id(node_id)
        row = RowWidget(self.fields, cells,
                        widths=self.col_widths,
                        communicator=self.communicator)
        self.rows_by_id[node_id] = row
        self.layout.addWidget(row)

    def _filled_cells_for_id(self, node_id: int) -> list:
        """Fill pattern with mapping for the given node_id; return list of cell configs."""
        # find item dict for this ID (if any)
        item = next((it for it in self.items if it.get("id") == node_id), {})
        # build mapping with defaults and all custom fields
        mapping = dict(item)
        mapping.setdefault("id", node_id)
        mapping.setdefault("name", self.name_by_id.get(node_id, f"Node {node_id}"))

        cells = []
        for tmpl in self.pattern_list:
            filled = self._fill_placeholders(tmpl, mapping)
            if isinstance(filled, dict) and "type" in filled:
                f2 = dict(filled)
                if self.communicator and "communicator" not in f2:
                    f2["communicator"] = self.communicator
                filled = f2
            cells.append(filled)
        return cells

    # ---------- helpers ----------
    @staticmethod
    def _to_key(label: str) -> str:
        import re
        s = re.sub(r"\s+", "_", str(label).strip().lower())
        s = re.sub(r"[^a-z0-9_]", "", s)
        return s or "col"

    @staticmethod
    def _sort_key(x):
        try:
            return (0, int(x))
        except Exception:
            return (1, str(x))

    def _fill_placeholders(self, obj, mapping: dict):
        """Recursively format strings in dict/list structures using mapping."""
        if isinstance(obj, str):
            try:
                return obj.format(**mapping)
            except KeyError:
                return obj  # leave unchanged if key missing
        elif isinstance(obj, dict):
            return {k: self._fill_placeholders(v, mapping) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._fill_placeholders(x, mapping) for x in obj]
        return obj

    def _header_based_widths(self, fm: QFontMetrics, headers: list[str]) -> list[int]:
        """Compute per-column widths using only header labels (like TableWidget baseline)."""
        widths = [0] * len(headers)
        for i, lbl in enumerate(headers):
            widths[i] = max(widths[i], fm.horizontalAdvance(str(lbl)))
        # small padding for cell margins
        return [w + 16 for w in widths]

    def closeEvent(self, e):
        if self._timer:
            self._timer.stop()
            self._timer = None
        super().closeEvent(e)

class BoundImage(QLabel):
    """
    A widget that displays one of two images depending on a field value
    from a subscribed topic.

    YAML example:
      type: BoundImage
      topics: [dronecan.uavcan.equipment.actuator.Status]
      fields: [power_rating_pct]
      node_id: 51
      threshold: 30
      image_low: "assets/low.png"
      image_high: "assets/high.png"
    """

    def __init__(self, cfg):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.communicator = cfg.get("communicator")
        if not self.communicator:
            return

        self.node_id = cfg.get("node_id")
        self.threshold = float(cfg.get("threshold", 30))
        self.image_low_path = cfg.get("image_low", "assets/low.png")
        self.image_high_path = cfg.get("image_high", "assets/high.png")

        # Load images
        self.image_low = QPixmap(self.image_low_path)
        self.image_high = QPixmap(self.image_high_path)

        if not self.image_low or self.image_low.isNull():
            logger.warning(f"Missing image_low: {self.image_low_path}")
        if not self.image_high or self.image_high.isNull():
            logger.warning(f"Missing image_high: {self.image_high_path}")

        # Initially show the "low" image
        self.current_image = self.image_low
        self.setPixmap(self._fit_pixmap(self.image_low))

        # Subscribe
        topics = cfg.get("topics")
        fields = cfg.get("fields")
        if topics and fields:
            self.topic_field_pairs = list(zip(topics, fields))
        else:
            topic = cfg.get("topic")
            field = cfg.get("field")
            self.topic_field_pairs = [(topic, field)] if topic and field else []

        for topic, field in self.topic_field_pairs:
            self.communicator.subscribe(
                dtype=topic,
                cb=lambda t, msg, f=field: self._on_msg(msg, f),
                node_id=self.node_id,
            )

    def _fit_pixmap(self, pixmap: QPixmap) -> QPixmap:
        """Scale image only if it exceeds the widget's current size."""
        if not pixmap or pixmap.isNull():
            return QPixmap()

        target_w = self.width() or 100
        target_h = self.height() or 100
        img_w = pixmap.width()
        img_h = pixmap.height()

        # Only scale down if needed
        if img_w > target_w or img_h > target_h:
            return pixmap.scaled(
                target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        return pixmap

    def resizeEvent(self, event):
        """Ensure image fits new cell size on resize."""
        if self.current_image and not self.current_image.isNull():
            self.setPixmap(self._fit_pixmap(self.current_image))
        super().resizeEvent(event)

    def _on_msg(self, msg, field):
        """Update image based on topic value."""
        value = msg.get(field) if isinstance(msg, dict) else getattr(msg, field, None)
        if value is None:
            return

        try:
            val = float(value)
        except (ValueError, TypeError):
            return

        new_image = self.image_high if val >= self.threshold else self.image_low
        if new_image.cacheKey() != self.current_image.cacheKey():
            self.current_image = new_image
            self.setPixmap(self._fit_pixmap(self.current_image))

    def sizeHint(self):
        """Return scaled image size or a reasonable default."""
        if self.current_image and not self.current_image.isNull():
            img_size = self.current_image.size()
            # Clamp to current widget or parent size to avoid oversized rows
            w = min(img_size.width(), self.width() or 32)
            h = min(img_size.height(), self.height() or 32)
            return QSize(w, h)
        return QSize(24, 24)


class PlotWidget(BaseWidget):
    """Real-time plotting widget that subscribes to topic fields and draws live data."""

    def init_ui(self):
        self.pg = lazy_import_module("PlotWidget", "pyqtgraph")
        self.communicator = self.cfg.get("communicator")
        self.topics = self.cfg.get("topics") or [self.cfg.get("topic")]
        self.fields = self.cfg.get("fields") or [self.cfg.get("field")]
        self.names = self.cfg.get("names", self.fields)
        self.node_id = self.cfg.get("node_id")
        self.window = int(self.cfg.get("window", 200))
        self.refresh_rate = float(self.cfg.get("refresh_rate", 20))
        self.title = self.cfg.get("title", None)
        self.xlabel = self.cfg.get("xlabel", "Samples")
        self.ylabel = self.cfg.get("ylabel", "Value")

        # Prepare data storage
        self.data = {f: deque(maxlen=self.window) for f in self.fields}
        self.xdata = deque(maxlen=self.window)
        self.counter = 0

        # Setup pyqtgraph widget
        self.plot_widget = self.pg.PlotWidget()
        self.plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_widget.setMinimumHeight(150)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        if self.title:
            self.plot_widget.setTitle(self.title)
        self.plot_widget.setLabel("bottom", self.xlabel)
        self.plot_widget.setLabel("left", self.ylabel)
        self.plot_widget.addLegend(offset=(10, 10))

        # Create curves
        self.curves = {}
        colors = ["y", "c", "m", "g", "r", "b"]

        for i, (f, name) in enumerate(zip(self.fields, self.names)):
            pen = self.pg.mkPen(colors[i % len(colors)], width=2)
            self.curves[f] = self.plot_widget.plot([], [], pen=pen, name=name)

        self.layout.addWidget(self.plot_widget)

        # Subscribe to topics
        if self.communicator and self.topics:
            for topic in self.topics:
                self.communicator.subscribe(dtype=topic, cb=lambda t, msg: self._on_msg(msg), node_id=self.node_id)

        # Timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_plot)
        self.timer.start(int(1000 / self.refresh_rate))

    def _on_msg(self, msg):
        """Handle incoming messages and store values."""
        from re import split as resplit

        self.counter += 1
        self.xdata.append(self.counter)

        for f in self.fields:
            val = resolve_field_path(msg, f)
            if isinstance(val, (int, float)):
                self.data[f].append(val)
            else:
                self.data[f].append(float("nan"))

    def _update_plot(self):
        """Redraw curves with latest samples."""
        for f, curve in self.curves.items():
            y = list(self.data[f])
            if not y:
                continue
            x = list(self.xdata)[-len(y):]
            curve.setData(x, y)

class HorizontalSliderWidget(BaseWidget):
    """Slider widget bound to a communicator topic/field.

    Config keys:
      - topic: topic name to listen/push to
      - field: field name inside messages
      - min, max, step, initial: integer slider range
      - unit: optional unit string displayed after value
      - text: optional label text
      - field_type: optional (int, float, bool)
      - multiplier: optional numeric multiplier
      - offset: optional numeric offset
    """

    def init_ui(self):
        cfg = self.cfg
        self.topic = cfg.get("topic")
        self.field = cfg.get("field")
        self.unit = cfg.get("unit", "")
        self.min = int(cfg.get("min", 0))
        self.max = int(cfg.get("max", 100))
        self.step = int(cfg.get("step", 1))
        self.value = int(cfg.get("initial", self.min))
        self.field_type = cfg.get("field_type")
        self.multiplier = cfg.get("multiplier")
        self.offset = cfg.get("offset")
        self.frequency = float(cfg.get("frequency", 1.0))

        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        self.label = QLabel()
        fm = QFontMetrics(self.label.font())
        widest_text = f"{self.max}{self.unit}"
        label_width = fm.horizontalAdvance(widest_text) + 10
        self.label.setFixedWidth(label_width)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label.setText(f"{self.value}{self.unit}")
        h.addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(self.min, self.max)
        self.slider.setSingleStep(self.step)
        self.slider.setValue(self.value)
        self.slider.valueChanged.connect(self._on_value_changed)
        h.addWidget(self.slider, 1)

        self.layout.addLayout(h)

        self.communicator = cfg.get("communicator")
        if self.communicator and self.topic:
            try:
                self.communicator.advertise(self.topic, self.field, self.frequency)
            except Exception as err:
                logger.critical(err)

    def _on_value_changed(self, value):
        if not self.communicator or not self.topic:
            self.label.setText("Err")
            return

        self.label.setText(f"{value}{self.unit}")

        value = self._apply_value_transforms(
            value,
            field_type=self.field_type,
            multiplier=self.multiplier,
            offset=self.offset,
        )

        self.communicator.set_publisher_field(dtype=self.topic, field=self.field, value=value)

class DialWidget(BaseWidget):
    """Rotary dial widget bound to a communicator topic/field.

    Config keys:
      - topic: topic name to listen/push to
      - field: field name inside messages
      - min, max, step, initial: numeric range (int or float)
      - unit: optional unit string displayed next to value
      - text: optional label text (title above the dial)
      - field_type: optional (int, float, bool)
      - multiplier: optional numeric multiplier
      - offset: optional numeric offset
      - suffix: optional label for actuator name
    """

    def init_ui(self):
        from PySide6.QtWidgets import QVBoxLayout, QLabel, QDial, QHBoxLayout

        cfg = self.cfg
        self.topic = cfg.get("topic")
        self.field = cfg.get("field")
        self.text_label = cfg.get("text", "")
        self.unit = cfg.get("unit", "")
        self.min = float(cfg.get("min", 0))
        self.max = float(cfg.get("max", 100))
        self.step = float(cfg.get("step", 1))
        self.value = float(cfg.get("initial", self.min))
        self.field_type = cfg.get("field_type")
        self.multiplier = cfg.get("multiplier")
        self.offset = cfg.get("offset")
        self.communicator = cfg.get("communicator")
        self.frequency = float(cfg.get("frequency", 1.0))

        # --- Layout ---
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        if self.text_label:
            title = QLabel(self.text_label)
            title.setAlignment(Qt.AlignCenter)
            v.addWidget(title)

        self.dial = QDial()
        self.dial.setRange(int(self.min / self.step), int(self.max / self.step))
        self.dial.setNotchesVisible(True)
        self.dial.setValue(int(self.value / self.step))
        self.dial.valueChanged.connect(self._on_value_changed)
        v.addWidget(self.dial, alignment=Qt.AlignCenter)

        # Label showing numeric value
        self.value_label = QLabel(f"{self.value:.0f}{self.unit}")
        self.value_label.setAlignment(Qt.AlignCenter)
        v.addWidget(self.value_label)

        self.layout.addLayout(v)

        # --- Communicator setup ---
        if self.communicator and self.topic:
            try:
                self.communicator.advertise(self.topic, self.field, self.frequency)
            except Exception as err:
                logger.critical(f"DialWidget advertise failed: {err}")

    def _on_value_changed(self, raw_steps):
        if not self.communicator or not self.topic:
            self.value_label.setText("Err")
            return

        value = raw_steps * self.step
        self.value_label.setText(f"{value:.1f}{self.unit}")

        transformed = self._apply_value_transforms(
            value,
            field_type=self.field_type,
            multiplier=self.multiplier,
            offset=self.offset,
        )

        self.communicator.set_publisher_field(
            dtype=self.topic,
            field=self.field,
            value=transformed,
        )

class PublisherWidget(BaseWidget):
    """
    Editable field that periodically publishes a value to a topic/field.

    Config keys:
      - topic, field, node_id, text, unit, frequency, initial (as before)
      - field_type: optional (int, float, bool)
      - multiplier: optional numeric multiplier
      - offset: optional numeric offset
    """

    def init_ui(self):
        from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit

        cfg = self.cfg
        self.topic = cfg.get("topic")
        self.field = cfg.get("field")
        self.node_id = cfg.get("node_id")
        self.text_label = cfg.get("text", "")
        self.unit = cfg.get("unit", "")
        self.frequency = float(cfg.get("frequency", 10.0))
        self.value = float(cfg.get("initial", 0))
        self.field_type = cfg.get("field_type")
        self.multiplier = cfg.get("multiplier")
        self.offset = cfg.get("offset")
        self.communicator = cfg.get("communicator")

        # Layout setup
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(4)

        if self.text_label:
            label = QLabel(self.text_label)
            h.addWidget(label)

        self.input = QLineEdit(str(self.value))
        self.input.setFixedWidth(80)
        self.input.setAlignment(Qt.AlignLeft)
        h.addWidget(self.input)

        if self.unit:
            unit_label = QLabel(self.unit)
            unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            h.addWidget(unit_label)

        self.layout.addLayout(h)

        if not self.communicator or not self.topic or not self.field:
            logger.warning("PublisherWidget: communicator/topic/field not set.")
            return

        try:
            self.communicator.advertise(self.topic, self.field, frequency=self.frequency)
        except Exception as err:
            logger.critical(f"Failed to advertise publisher {self.topic}.{self.field}: {err}")
            return

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._publish_current_value)
        self.timer.start(int(1000 / self.frequency))

        self.input.editingFinished.connect(self._on_user_edit)
        self.input.returnPressed.connect(self._on_user_edit)

    def _on_user_edit(self):
        """Update current value when user edits the field."""
        text = self.input.text().strip()
        if not text:
            return
        try:
            self.value = float(text)
        except ValueError:
            logger.warning(f"Invalid input for {self.topic}.{self.field}: '{text}'")
            return
        self._publish_current_value()

    def _publish_current_value(self):
        """Send the current value through communicator."""
        if not self.communicator or not self.topic or not self.field:
            return

        value = self._apply_value_transforms(
            self.value,
            field_type=self.field_type,
            multiplier=self.multiplier,
            offset=self.offset,
        )

        try:
            self.communicator.set_publisher_field(self.topic, self.field, value)
        except Exception as e:
            logger.error(f"Failed to publish {self.topic}.{self.field}: {e}")

class CanGraphWidget(BaseWidget):
    """Visualizes CAN topology (nodes, hubs, connections) as a graph."""

    def init_ui(self):
        self.pg = lazy_import_module("CanGraphWidget", "pyqtgraph")
        self.communicator = self.cfg.get("communicator")
        self.topology = self.cfg.get("topology", {})
        self.refresh_rate = float(self.cfg.get("refresh_rate", 2))

        # Prepare graph view
        self.graph_widget = self.pg.GraphItem()
        self.plot = self.pg.PlotWidget()
        self.plot.setAspectLocked(True)
        self.plot.hideAxis('bottom')
        self.plot.hideAxis('left')
        self.plot.addItem(self.graph_widget)
        self.layout.addWidget(self.plot)

        # Periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_graph)
        self.timer.start(int(1000 / self.refresh_rate))

        self.text_items = []

        self._update_graph()

    def _update_graph(self):
        """Draw or refresh graph based on topology."""
        elements = self.topology.get("elements", [])
        connections = self.topology.get("connections", [])

        # Build node map
        ids = [str(e["id"]) for e in elements]
        names = [e.get("name", str(e["id"])) for e in elements]
        colors = []
        for e in elements:
            if e.get("type") in ("mixer", "hub", "repeater"):
                colors.append((150, 150, 255, 255))  # bluish
            else:
                colors.append((150, 255, 150, 255))  # greenish

        n = len(ids)
        pos = {i: (i % 5, i // 5) for i in range(n)}  # simple grid layout
        adj = []
        for c in connections:
            if len(c) == 2 and str(c[0]) in ids and str(c[1]) in ids:
                i1, i2 = ids.index(str(c[0])), ids.index(str(c[1]))
                adj.append((i1, i2))

        # Convert to arrays
        import numpy as np
        pos_array = np.array([pos[i] for i in range(n)])
        adj_array = np.array(adj)
        symbols = ["o" if "node" in elements[i]["type"] else "s" for i in range(n)]
        brushes = [self.pg.mkBrush(*c) for c in colors]

        self.graph_widget.setData(
            pos=pos_array,
            adj=adj_array,
            symbol=symbols,
            size=20,
            pxMode=True,
            brush=brushes,
            pen="w",
            texts=names,
            textPen="w"
        )

        # Clear old labels
        for t in self.text_items:
            self.plot.removeItem(t)
        self.text_items.clear()

        # Add text labels near each node
        for (x, y), name in zip(pos_array, names):
            label = self.pg.TextItem(text=name, color=(230, 230, 230), anchor=(0.5, -0.3))
            label.setPos(x, y)
            self.plot.addItem(label)
            self.text_items.append(label)
