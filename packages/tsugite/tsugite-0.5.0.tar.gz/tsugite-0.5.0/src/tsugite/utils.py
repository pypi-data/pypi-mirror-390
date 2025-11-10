#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>
"""
Utils
"""
import re
import logging
import importlib
import collections.abc

logger = logging.getLogger(__name__)

def resolve_field_path(obj, field_path: str):
    """
    Resolve a nested/indexed field path such as:
      - "timestamp.usec"
      - "accelerometer_integral[0]"
      - "data.vector[2].x"

    Works for both dicts and objects with attributes.
    Returns None if any intermediate attribute is missing.
    """
    if obj is None or not field_path:
        return None

    parts = re.split(r"\.(?![^\[]*\])", field_path)
    cur = obj

    for part in parts:
        if cur is None:
            return None

        # Match 'name[3]'
        m = re.match(r"([A-Za-z0-9_]+)\[(\d+)\]$", part)
        if m:
            attr, idx = m.groups()
            idx = int(idx)
            cur = getattr(cur, attr, None) if not isinstance(cur, dict) else cur.get(attr)

            # handle both lists, tuples, and "array-like" objects
            if isinstance(cur, collections.abc.Sequence) or hasattr(cur, "__getitem__"):
                try:
                    cur = cur[idx]
                except (IndexError, TypeError):
                    return None
            else:
                return None
        else:
            cur = getattr(cur, part, None) if not isinstance(cur, dict) else cur.get(part)

    return cur

def data_type_name_to_obj(dtype: str):
    if not isinstance(dtype, str):
        raise ValueError("Data type must be a string")

    try:
        parts = dtype.split(".")
        module = importlib.import_module(parts[0])
        data_type = module
        for p in parts[1:]:
            data_type = getattr(data_type, p)
    except (ModuleNotFoundError, AttributeError) as e:
        logger.error("Failed to resolve topic '%s': %s", dtype, e)
        return None

    return data_type

def make_field_setter(root, path: str):
    """Returns a lightweight lambda that sets a nested field efficiently."""
    parts = re.split(r'\.(?![^[]*\])', path)  # split on '.' ignoring inside brackets

    # Resolve the object and final attribute/index once
    def resolve_parent():
        target = root
        for part in parts[:-1]:
            match = re.match(r'(\w+)\[(\d+)\]', part)
            if match:
                name, idx = match.groups()
                target = getattr(target, name)[int(idx)]
            else:
                target = getattr(target, part)
        return target, parts[-1]

    # Resolve once, build direct setter to target attr
    target, last = resolve_parent()
    match = re.match(r'(\w+)\[(\d+)\]', last)
    if match:
        name, idx = match.groups()
        seq = getattr(target, name)
        current = seq[int(idx)]
        attr_type = type(current)
        return lambda val, s=seq, i=int(idx), t=attr_type: s.__setitem__(i, t(val))

    current = getattr(target, last, None)
    attr_type = type(current) if current is not None else type
    return lambda val, o=target, a=last, t=attr_type: setattr(o, a, t(val))
