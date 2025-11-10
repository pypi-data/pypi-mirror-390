#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>

from __future__ import annotations
from pathlib import Path
from typing import Iterable, Optional
import os
import yaml
from importlib.resources import files, as_file  # py>=3.9

__all__ = ["load_yaml_with_includes"]

_ENV_EXTRA_ROOTS = "TSUGITE_CONFIG_PATHS"

class _IncludeLoader(yaml.SafeLoader):
    """YAML loader that supports !include relative to the current file,
    absolute paths, optional extra roots, and packaged resources.
    """
    def __init__(self, stream, root: Path, extra_roots: tuple[Path, ...]):
        super().__init__(stream)
        self._root = root
        self._extra_roots = extra_roots

def _open_packaged_resource(relpath: str):
    res = files("tsugite.configs").joinpath(relpath)
    return None if not res.exists() else as_file(res)

def _construct_include(loader: yaml.SafeLoader, node: yaml.Node):
    rel = loader.construct_scalar(node)
    candidate = Path(rel)

    # 1) absolute
    if candidate.is_absolute() and candidate.exists():
        with candidate.open("r", encoding="utf-8") as f:
            return yaml.load(f, Loader=lambda s: _IncludeLoader(s, candidate.parent, loader._extra_roots))

    # 2) relative to including file
    local = (loader._root / rel).resolve()
    if local.exists():
        with local.open("r", encoding="utf-8") as f:
            return yaml.load(f, Loader=lambda s: _IncludeLoader(s, local.parent, loader._extra_roots))

    # 3) extra search roots (CLI flag or env)
    for root in loader._extra_roots:
        p = (root / rel).resolve()
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                return yaml.load(f, Loader=lambda s: _IncludeLoader(s, p.parent, loader._extra_roots))

    # 4) packaged fallback (inside wheel)
    ctx = _open_packaged_resource(rel)
    if ctx is not None:
        with ctx as path:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.load(f, Loader=lambda s: _IncludeLoader(s, Path(path).parent, loader._extra_roots))

    raise FileNotFoundError(f"!include not found (absolute/relative/extra_roots/packaged): {rel}")

def load_yaml_with_includes(path: Path, extra_roots: Optional[Iterable[Path]] = None) -> dict:
    """Load YAML with support for !include.
    - `path`: top-level config file
    - `extra_roots`: optional directories to search before packaged fallback
    - env var TSUGITE_CONFIG_PATHS="dir1:dir2" is also honored
    """
    roots: tuple[Path, ...] = tuple(Path(r).resolve() for r in (extra_roots or ()))
    if _ENV_EXTRA_ROOTS in os.environ:
        env_roots = [Path(p).expanduser().resolve() for p in os.environ[_ENV_EXTRA_ROOTS].split(os.pathsep) if p]
        roots = tuple(list(roots) + env_roots)

    _IncludeLoader.add_constructor("!include", _construct_include)
    with path.open("r", encoding="utf-8") as f:
        return yaml.load(f, Loader=lambda s: _IncludeLoader(s, path.parent.resolve(), roots)) or {}
