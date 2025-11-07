"""Common types and utilities for the datastore."""

from types import NoneType

ValueType = str | int | float | list | bool | NoneType
"""Allowed runtime value types for settings and records."""

PossibleTypes = type[bool] | type[int] | type[float] | type[str] | type[NoneType] | type[list]
"""Python types corresponding to ValueType."""

UNIFIED_DATA_VERSION = "0.1.0"
"""The current version of the unified data format."""


__all__ = ["PossibleTypes", "ValueType"]
