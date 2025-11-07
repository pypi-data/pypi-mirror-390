"""Tests for SettingsManager with WAL integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from bear_dereth.config.settings_manager import BearSettings, SettingsManager
from bear_dereth.datastore.wal_config import WALConfig


def test_settings_manager_wal_disabled_by_default(tmp_path: Path):
    """Test that WAL is disabled by default for SettingsManager."""
    settings = SettingsManager("test_app", path=tmp_path)

    # Access db to trigger creation
    _ = settings.db

    # WAL should be disabled by default (uses dummy helper)
    table = settings.table
    from bear_dereth.datastore.tables.table import WALHelperDummy

    assert isinstance(table.wal_helper, WALHelperDummy)
    assert not table.enable_wal

    settings.close()


def test_settings_manager_wal_enabled_with_flag(tmp_path: Path):
    """Test enabling WAL with enable_wal flag."""
    settings = SettingsManager("test_app", path=tmp_path, enable_wal=True)

    # Access db to trigger creation
    _ = settings.db

    # WAL should be enabled
    table = settings.table
    assert table.wal_helper is not None
    assert table.enable_wal

    # Set some settings
    settings.set("key1", "value1")
    settings.set("key2", 42)
    settings.set("key3", value=True)

    assert len(settings) == 3
    assert settings.get("key1") == "value1"
    assert settings.get("key2") == 42
    assert settings.get("key3") is True

    settings.close()


def test_settings_manager_wal_with_config_object(tmp_path: Path):
    """Test WAL with full config object."""
    config = WALConfig.buffered(flush_interval=0.1, flush_batch_size=10)

    settings = BearSettings("test_app", path=tmp_path, enable_wal=True, wal_config=config)

    # Access db to trigger creation
    _ = settings.db

    # WAL should be enabled with config
    table = settings.table
    assert table.wal_helper is not None
    assert table.wal_helper._wal.config.flush_interval == 0.1
    assert table.wal_helper._wal.config.flush_batch_size == 10

    settings.close()


def test_settings_manager_wal_with_kwargs(tmp_path: Path):
    """Test WAL with individual kwargs."""
    settings = SettingsManager(
        "test_app",
        path=tmp_path,
        enable_wal=True,
        flush_mode="immediate",
        flush_interval=0.5,
    )

    # Access db to trigger creation
    _ = settings.db

    # WAL should be enabled with kwargs
    table = settings.table
    assert table.wal_helper is not None
    assert str(table.wal_helper._wal.config.flush_mode) == "immediate"
    assert table.wal_helper._wal.config.flush_interval == 0.5

    settings.close()


def test_settings_manager_bulk_operations_with_wal(tmp_path: Path):
    """Test bulk settings operations with WAL enabled."""
    settings = SettingsManager(
        "test_app",
        path=tmp_path,
        enable_wal=True,
        flush_mode="buffered",
        flush_batch_size=10,
    )

    # Bulk insert many settings
    for i in range(100):
        settings.set(f"setting_{i}", f"value_{i}")

    # Wait for WAL to flush
    if settings.table.wal_helper:
        assert settings.table.wal_helper.wait_for_idle()

    # Verify all settings are present
    assert len(settings) == 100

    # Verify retrieval works
    assert settings.get("setting_0") == "value_0"
    assert settings.get("setting_50") == "value_50"
    assert settings.get("setting_99") == "value_99"

    # Verify keys() works
    keys = settings.keys()
    assert len(keys) == 100
    assert "setting_0" in keys
    assert "setting_99" in keys

    settings.close()


def test_settings_manager_wal_dir_parameter(tmp_path: Path):
    """Test that wal_dir parameter is accepted and WAL is enabled."""
    wal_dir = tmp_path / "custom_wal_dir"
    wal_dir.mkdir()

    # Verify wal_dir parameter is accepted without error
    settings = SettingsManager(
        "test_app",
        path=tmp_path,
        enable_wal=True,
        wal_dir=str(wal_dir),
    )

    # Verify WAL is enabled
    table = settings.table
    assert table.wal_helper is not None
    assert table.enable_wal

    # Set a value and verify it works
    settings.set("test_key", "test_value")
    assert settings.get("test_key") == "test_value"

    settings.close()


def test_settings_manager_context_manager_with_wal(tmp_path: Path):
    """Test SettingsManager context manager with WAL."""
    from bear_dereth.config.settings_manager import settings

    with settings("test_app", path=tmp_path, enable_wal=True) as sm:
        sm.set("key1", "value1")
        sm.set("key2", 42)

        assert sm.get("key1") == "value1"
        assert sm.get("key2") == 42

    # Should be closed after context
    assert sm.closed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ruff: noqa: PLC0415
