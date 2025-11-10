#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>

import importlib
import logging
from PySide6.QtCore import QUrl, QTimer, QSize
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QVBoxLayout, QSizePolicy
from tsugite.ui.desktop.base_widget import BaseWidget

logger = logging.getLogger("gps_widget")


class _LoggingPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        lvl_map = {
            QWebEnginePage.InfoMessageLevel: "INFO",
            QWebEnginePage.WarningMessageLevel: "WARNING",
            QWebEnginePage.ErrorMessageLevel: "ERROR",
        }
        lvl = lvl_map.get(level, "INFO")
        logger.log(getattr(logging, lvl), f"[JS:{lvl}] {sourceID}:{lineNumber} {message}")

class GpsWidget(BaseWidget):
    """
    Minimal GPS map (no blinking):
      - Renders Leaflet once via setHtml().
      - Moves marker via JS on each message.
      - Pans only if marker leaves current view.

    Extra config (optional):
      - min_height: default 260 (ensures widget is tall enough in splitters/layouts)
      - zoom_start: default 14
      - recenter_if_out_of_view: default True
    """

    # --- sizing hints so splitters/layouts give us real space ---
    def sizeHint(self):
        h = int(self.cfg.get("min_height", 260)) if hasattr(self, "cfg") else 260
        return QSize(480, h)

    def minimumSizeHint(self):
        return QSize(320, int(self.cfg.get("min_height", 260)) if hasattr(self, "cfg") else 260)

    def init_ui(self):
        # --- Layout ---
        if not hasattr(self, "layout"):
            self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- WebView ---
        QWebEngineWidgets = importlib.import_module("PySide6.QtWebEngineWidgets")
        QWebEngineCore = importlib.import_module("PySide6.QtWebEngineCore")
        self.QWebEngineView = getattr(QWebEngineWidgets, "QWebEngineView")
        self.QWebEngineSettings = getattr(QWebEngineCore, "QWebEngineSettings")

        self.view = self.QWebEngineView(self)
        self.view.setPage(_LoggingPage(self.view))  # capture JS console
        s = self.view.settings()
        s.setAttribute(self.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(self.QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        # Ask the layout/splitter for space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(int(self.cfg.get("min_height", 260)))

        self.layout.addWidget(self.view)

        # --- Config ---
        cfg = self.cfg
        self.communicator = cfg.get("communicator")
        self.topic = cfg.get("topic")
        self.field_lat = cfg.get("field_lat", "lat")
        self.field_lon = cfg.get("field_lon", "lon")
        self.node_id = cfg.get("node_id")

        self.multiplier = float(cfg.get("multiplier", 1.0))
        self.offset_lat = float(cfg.get("offset_lat", 0.0))
        self.offset_lon = float(cfg.get("offset_lon", 0.0))

        self.zoom_start = int(cfg.get("zoom_start", 14))
        self.recenter_if_out = bool(cfg.get("recenter_if_out_of_view", True))

        # --- State ---
        self._page_ready = False
        self._first_fix = True
        self._pending = None  # (lat, lon, force_center)

        # Load minimal HTML directly (no temp files)
        html = self._leaflet_html(0.0, 0.0, self.zoom_start)
        self.view.setHtml(html, baseUrl=QUrl("https://unpkg.com/"))
        self.view.loadFinished.connect(self._on_load_finished)

        # --- Subscribe ---
        if self.communicator and self.topic:
            self.communicator.subscribe(dtype=self.topic, cb=self._on_msg, node_id=self.node_id)

    # Ensure Leaflet recalculates tiles when we’re resized by splitters/layouts
    def resizeEvent(self, e):
        super().resizeEvent(e)
        if getattr(self, "_page_ready", False):
            QTimer.singleShot(0, lambda: self.view.page().runJavaScript("map.invalidateSize();"))

    # ---------------- HTML ----------------
    def _leaflet_html(self, lat, lon, zoom):
        # The map div fills the whole page; Leaflet gets an explicit invalidateSize on resizes.
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="initial-scale=1, width=device-width"/>
<title>GPS</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
  html, body {{ height:100%; margin:0; padding:0; }}
  #map {{ position:absolute; inset:0; }} /* fill container */
  .leaflet-container {{ background:#f0f0f0; }}
</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  const map = L.map('map', {{ zoomControl:true }}).setView([{lat}, {lon}], {zoom});
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);

  const gpsIcon = L.icon({{
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25,41], iconAnchor: [12,41], popupAnchor: [1,-34], shadowSize: [41,41]
  }});

  const gpsMarker = L.marker([{lat}, {lon}], {{ icon:gpsIcon, title:'GPS' }}).addTo(map);

  function recenterIfNeeded() {{
    const inside = map.getBounds().contains(gpsMarker.getLatLng());
    if (!inside) map.panTo(gpsMarker.getLatLng(), {{ animate:true }});
  }}

  window.updateMarker = function(lat, lon, forceCenter) {{
    gpsMarker.setLatLng([lat, lon]);
    if (forceCenter) {{
      map.setView([lat, lon], map.getZoom());
    }} else {{
      recenterIfNeeded();
    }}
  }}

  // If the container changes size after load, make Leaflet relayout.
  window.addEventListener('resize', () => map.invalidateSize());
  setTimeout(() => map.invalidateSize(), 0);
</script>
</body>
</html>"""

    # ---------------- Page/JS bridge ----------------
    def _on_load_finished(self, ok: bool):
        self._page_ready = bool(ok)
        if not ok:
            logger.error("GPS map failed to load (loadFinished=False). Check network/CDN access.")
            return
        # Ensure correct layout after initial paint
        QTimer.singleShot(0, lambda: self.view.page().runJavaScript("map.invalidateSize();"))
        if self._pending is not None:
            lat, lon, force_center = self._pending
            self._pending = None
            self._js_update(lat, lon, force_center)

    def _js_update(self, lat: float, lon: float, force_center: bool):
        if not self._page_ready:
            self._pending = (lat, lon, force_center)
            return
        self.view.page().runJavaScript(
            f"window.updateMarker({lat:.8f}, {lon:.8f}, {str(force_center).lower()});"
        )

    # ---------------- Incoming data ----------------
    def _on_msg(self, topic, msg):
        lat = getattr(msg, self.field_lat, None) if not isinstance(msg, dict) else msg.get(self.field_lat)
        lon = getattr(msg, self.field_lon, None) if not isinstance(msg, dict) else msg.get(self.field_lon)
        if lat is None or lon is None:
            return
        try:
            lat = float(lat) * self.multiplier + self.offset_lat
            lon = float(lon) * self.multiplier + self.offset_lon
        except (ValueError, TypeError):
            logger.warning(f"Invalid GPS data: lat={lat}, lon={lon}")
            return

        force_center = self._first_fix
        self._first_fix = False
        self._js_update(lat, lon, force_center)
