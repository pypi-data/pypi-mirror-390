#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>
"""
"""

import sys
import signal
import logging
import argparse
from pathlib import Path
import urllib.request

# Restore the default OS behavior for SIGINT (Ctrl+C).
# Without it, Qt overrides Python’s signal handling,
# so pressing Ctrl+C does nothing until you close the window manually.
signal.signal(signal.SIGINT, signal.SIG_DFL)

logger = logging.getLogger(__name__)

try:
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QHBoxLayout,
        QWidget,
        QStackedWidget,
        QSizePolicy,
    )
    from PySide6.QtCore import Qt, QTimer, QSize
    from PySide6.QtGui import QKeySequence, QShortcut, QPixmap, QIcon
except ModuleNotFoundError:
    logger.critical("PySide6 required: pip install PySide6>=6.10.0")
    sys.exit(1)

from tsugite.ui.desktop.widgets import WidgetFactory, TableWidget
from tsugite.loader import load_yaml_with_includes
from tsugite.backend.backend import instanciate_backend, BackendInitializationError
from tsugite.ui.desktop.welcome_panel import WelcomePanel


class MainWindow(QMainWindow):
    def __init__(self, config: dict, communicator: object):
        super().__init__()
        self.config = config
        self.communicator = communicator

        self.setWindowTitle(self.config.get("metadata", {}).get("project", "Tsugite"))
        self.resize(600, 400)
        main_layout = QVBoxLayout()

        # Navigation Bar between Panels
        self.nav_bar_buttons = []
        nav_bar = QHBoxLayout()

        self.stack = QStackedWidget()

        # --- Add Welcome Panel first ---
        welcome_panel = WelcomePanel(
            config=self.config,
            communicator=self.communicator,
            reload_callback=lambda: self._reload_config(),
            reconnect_callback=lambda: self._reconnect_backend(),
        )
        self.stack.addWidget(welcome_panel)

        welcome_btn = QPushButton("Welcome")
        welcome_btn.setCheckable(True)
        welcome_btn.clicked.connect(lambda checked=False: self.switch_panel(0))
        self.nav_bar_buttons.append(welcome_btn)
        nav_bar.addWidget(welcome_btn)

        for idx, (panel_name, panel_info) in enumerate(self.config["panels"].items(), start=1):
            btn = QPushButton(panel_name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self.switch_panel(i))

            # --- optional icon support ---
            icon_path = panel_info.get("icon")
            icon_url = panel_info.get("icon_url")
            if icon_path:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    btn.setIcon(QIcon(pixmap))
                    btn.setIconSize(QSize(20, 20))
            elif icon_url:
                try:
                    data = urllib.request.urlopen(icon_url).read()
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    if not pixmap.isNull():
                        btn.setIcon(QIcon(pixmap))
                        btn.setIconSize(QSize(20, 20))
                except Exception as e:
                    logger.warning(f"Failed to download icon for '{panel_name}': {e}")

            self.nav_bar_buttons.append(btn)
            nav_bar.addWidget(btn)
            self.stack.addWidget(self.create_panel(panel_info))

        main_layout.addLayout(nav_bar)
        main_layout.addWidget(self.stack)

        # --- Select Welcome panel by default ---
        if self.nav_bar_buttons:
            self.nav_bar_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)

        # --- Alt+1..9 shortcuts for fast switching ---
        for i in range(1, min(10, self.stack.count() + 1)):
            shortcut = QShortcut(QKeySequence(f"Alt+{i}"), self)
            shortcut.activated.connect(lambda checked=False, idx=i - 1: self.switch_panel(idx))

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_panel(self, panel_info: dict) -> QWidget:
        """Dynamically create a QWidget based on panel definition."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignTop)

        for widget_cfg in panel_info.get("widgets", []):
            widget_cfg["communicator"] = self.communicator # HACK: pass communicator to widgets
            widget = WidgetFactory.create(widget_cfg)
            if isinstance(widget, TableWidget):
                widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            layout.addWidget(widget)

        panel.setLayout(layout)
        return panel

    def switch_panel(self, index: int):
        """Switch visible panel by index."""
        for i, btn in enumerate(self.nav_bar_buttons):
            btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)

    def _reload_config(self):
        logger.info("Reload config not implemented yet")

    def _reconnect_backend(self):
        logger.info("Reconnect backend not implemented yet")


def main(args: argparse.Namespace) -> None:
    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger.setLevel(logging_level)

    config_path = args.config
    if config_path.exists():
        config_path = args.config
    else:
        tsugite_dir = Path(__file__).resolve().parent.parent.parent
        example_config = tsugite_dir / args.config
        if example_config.exists():
            config_path = example_config
        else:
            logger.critical("YAML config not found: %s / %s", args.config, example_config)
            sys.exit(1)

    try:
        config = load_yaml_with_includes(config_path)
    except Exception as e:
        logger.error(f"Failed to load YAML: {e}")
        sys.exit(1)

    app = QApplication()

    try:
        communicator = instanciate_backend(args.backend, args.iface, args.node_id)
    except BackendInitializationError as e:
        logger.critical(str(e))
        sys.exit(1)

    window = MainWindow(config, communicator)
    window.show()

    TICK_HZ = 100
    timer = QTimer()
    timer.timeout.connect(lambda: communicator.tick(1.0 / TICK_HZ))
    timer.start(int(1000 / TICK_HZ))  # milliseconds per tick

    sys.exit(app.exec())
