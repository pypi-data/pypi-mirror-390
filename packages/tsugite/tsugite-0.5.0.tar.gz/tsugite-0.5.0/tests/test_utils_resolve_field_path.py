#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>

import pytest

from tsugite.utils import resolve_field_path


class DummyDataType:
    def __init__(self):
        self.value = 42
        self.timestamp = DummyTimestamp()
        self.data = {
            "vector": [DummyVector(1), DummyVector(2), DummyVector(3)]
        }
        self.accelerometer_integral = [10, 20, 30]


class DummyTimestamp:
    def __init__(self):
        self.usec = 123456


class DummyVector:
    def __init__(self, x):
        self.x = x
        self.y = x + 10


class ArrayLike:
    """Custom object that mimics an array with __getitem__ but is not a list."""
    def __init__(self, values):
        self._values = values

    def __getitem__(self, idx):
        return self._values[idx]


def test_simple_attribute_access():
    obj = DummyDataType()
    assert resolve_field_path(obj, "value") == 42


def test_nested_attribute_access():
    obj = DummyDataType()
    assert resolve_field_path(obj, "timestamp.usec") == 123456


def test_dict_access():
    obj = DummyDataType()
    assert resolve_field_path(obj, "data.vector[1].x") == 2


def test_indexed_list_access():
    obj = DummyDataType()
    assert resolve_field_path(obj, "accelerometer_integral[2]") == 30


def test_indexed_arraylike_access():
    obj = DummyDataType()
    obj.custom_array = ArrayLike([100, 200, 300])
    assert resolve_field_path(obj, "custom_array[1]") == 200


def test_missing_attribute_returns_none():
    obj = DummyDataType()
    assert resolve_field_path(obj, "missing") is None
    assert resolve_field_path(obj, "timestamp.missing") is None


def test_index_out_of_range_returns_none():
    obj = DummyDataType()
    assert resolve_field_path(obj, "accelerometer_integral[5]") is None


def test_empty_field_or_none_obj_returns_none():
    assert resolve_field_path(None, "something") is None
    obj = DummyDataType()
    assert resolve_field_path(obj, "") is None


def test_nested_dict_mixed_with_attrs():
    obj = {
        "outer": DummyDataType()
    }
    assert resolve_field_path(obj, "outer.timestamp.usec") == 123456


def test_complex_chain():
    obj = DummyDataType()
    assert resolve_field_path(obj, "data.vector[0].y") == 11


if __name__ == "__main__":
    pytest.main([__file__])
