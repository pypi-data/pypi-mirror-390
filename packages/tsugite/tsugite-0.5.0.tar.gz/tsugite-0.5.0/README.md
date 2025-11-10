# Tsugite [![PyPI](https://img.shields.io/pypi/v/tsugite?logo=pypi&style=flat)](https://pypi.org/project/tsugite/) [![TestPyPI](https://img.shields.io/pypi/v/tsugite?label=TestPyPI&logo=pypi&pypiBaseUrl=https://test.pypi.org&include_prereleases=true&style=flat)](https://test.pypi.org/project/tsugite/) ![coverage](https://img.shields.io/badge/dynamic/json?url=https://gist.githubusercontent.com/ponomarevda/20c5b223bf0056aa734fec26e21d939d/raw/coverage.json&label=coverage&query=$.coverage&color=blue) [![Downloads](https://static.pepy.tech/badge/tsugite)](https://pepy.tech/project/tsugite)

A system-oriented dashboard for Cyphal (CAN + UDP) & DroneCAN. Render live panels from a YAML manifest - so you watch the system, not just the bus.

> 🪵 “Tsugite” (継ぎ手) - a Japanese word for traditional wood joinery - symbolizes how separate modules fit together into one solid structure, just like nodes in your robotics system.

## Why this exists

Most tools are **bus-oriented** (frames/subjects). Field work needs **system-oriented** views:
- “Is my **VTOL** healthy? Which **nodes** are missing?
- "Are **critical topics** alive?”
- “Can I monitor it remotely - from my laptop or tablet?”

Tsugite answers with:
- A **YAML system manifest** that defines your expected nodes, panels, and topics.
- A **backend** that speaks Cyphal (CAN + UDP) & DroneCAN.
- A desktop GUI (PySide6) that dynamically renders dashboards (More frontends are considered to be added later).

## Usage

Latest stable version:

```bash
pip install "tsugite[dronecan]"

tsugite --help
```

Latest test version:

```bash
pip install -i https://test.pypi.org/simple/ "tsugite[dronecan]"
```

For devs:

```bash
git clone git@github.com:PonomarevDA/tsugite.git
pip install .[all]
```

## MVP scope

- ✅ **Transports**: SocketCAN / SLCAN (Linux, macOS, Windows where supported), UDP (Cyphal).
- ✅ **Protocols**: Cyphal, DroneCAN.
- ✅ **YAML manifest**: Define nodes, panels, widgets, and data bindings.
- ✅ **Widgets**: Dynamic system panels with labels, buttons, GPS, and plotting.
- ✅ **Node list**: Health, uptime, firmware version, voltages, temperature, and bootloader state.
- ✅ **Parameters panel**: Inspect and modify node parameters.
- ✅ **Component QA** (Node-level, active): run automated node-level tests to verify firmware, parameters, and behavior compliance — ensuring each device meets specification before deployment.
- ✅ **Bus analysis** (System-level, passive): review overall system traffic, measure total and per-node bandwidth, and detect missing frames or termination issues — a non-intrusive pre-flight consistency check.
- ✅ **CLI launcher**: `tsugite` or `python -m tsugite.cli` to run the GUI.
