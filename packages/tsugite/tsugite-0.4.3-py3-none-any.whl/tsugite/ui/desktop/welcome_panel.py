#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>

import logging
import platform
import webbrowser
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, QTimer

logger = logging.getLogger(__name__)


class WelcomePanel(QWidget):
    """Welcome/info panel displayed on app startup."""

    def __init__(self, config, communicator, reload_callback=None, reconnect_callback=None):
        super().__init__()
        self.config = config
        self.communicator = communicator
        self.reload_callback = reload_callback
        self.reconnect_callback = reconnect_callback

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Title / version ---
        metadata = config.get("metadata", {})
        project = metadata.get("project", "Tsugite")
        version = metadata.get("version", "unknown")
        desc = metadata.get("description", "")

        title = QLabel(f"<h1 style='margin-bottom:0'>{project}</h1>")
        subtitle = QLabel(f"<i>Version {version}</i>")
        subtitle.setStyleSheet("color: #aaa;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        if desc:
            desc_label = QLabel(desc.strip())
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        layout.addWidget(self._divider())

        # --- Connection info ---
        backend_name = getattr(communicator, "backend_name", "Unknown")
        iface = getattr(communicator, "iface", "-")
        status_label = QLabel(f"<b>Backend:</b> {backend_name}<br><b>Interface:</b> {iface}")
        status_label.setTextFormat(Qt.RichText)
        layout.addWidget(status_label)

        # --- System info ---
        sys_label = QLabel(
            f"<b>Python:</b> {platform.python_version()}<br>"
            f"<b>OS:</b> {platform.system()} {platform.release()}"
        )
        sys_label.setTextFormat(Qt.RichText)
        layout.addWidget(sys_label)

        # --- Buttons row ---
        btns = QHBoxLayout()
        btns.setSpacing(10)

        reload_btn = QPushButton("Reload Config")
        reload_btn.clicked.connect(self._reload_config)
        btns.addWidget(reload_btn)

        reconnect_btn = QPushButton("Reconnect")
        reconnect_btn.clicked.connect(self._reconnect)
        btns.addWidget(reconnect_btn)

        open_logs_btn = QPushButton("Open Logs")
        open_logs_btn.clicked.connect(self._open_logs)
        btns.addWidget(open_logs_btn)

        github_btn = QPushButton("GitHub")
        github_btn.clicked.connect(lambda: webbrowser.open("https://github.com/ponomarevda/tsugite"))
        btns.addWidget(github_btn)

        btns.addStretch()
        layout.addLayout(btns)

        layout.addWidget(self._divider())

        # --- Optional dynamic info from communicator ---
        self.dynamic_label = QLabel("Awaiting CAN activity...")
        self.dynamic_label.setStyleSheet("color: #888;")
        layout.addWidget(self.dynamic_label)

        layout.addStretch()

        # --- Shortcut hint ---
        hint = QLabel("💡 Tip: Use <b>ALT + N</b> to switch between panels.")
        hint.setStyleSheet("color: #666; font-size: 12px; margin-top: 15px;")
        hint.setAlignment(Qt.AlignRight)
        layout.addWidget(hint)

        self.setLayout(layout)

        # --- Periodic status refresh ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_status)
        self.timer.start(1000)

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #444;")
        return line

    def _update_status(self):
        """Update status line from communicator, if available."""
        if hasattr(self.communicator, "get_status_summary"):
            text = self.communicator.get_status_summary()
        else:
            text = None
        self.dynamic_label.setText(text or "Idle — no data received yet")

    def _reload_config(self):
        if self.reload_callback:
            self.reload_callback()

    def _reconnect(self):
        if self.reconnect_callback:
            self.reconnect_callback()
        elif hasattr(self.communicator, "reconnect"):
            try:
                self.communicator.reconnect()
            except Exception as e:
                logger.error(f"Reconnect failed: {e}")

    def _open_logs(self):
        logs_dir = Path.home() / ".tsugite" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        webbrowser.open(str(logs_dir))
