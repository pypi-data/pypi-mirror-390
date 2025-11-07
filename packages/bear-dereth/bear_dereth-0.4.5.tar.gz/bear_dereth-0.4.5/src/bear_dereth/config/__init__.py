"""Config and settings management utilities for Bear Utils."""

from bear_dereth.config._base_settings import BaseSettingHandler, TableWrapper
from bear_dereth.config.config_manager import ConfigManager
from bear_dereth.config.dir_manager import (
    DirectoryManager,
    clear_temp_directory,
    get_cache_path,
    get_config_path,
    get_local_config_path,
    get_settings_path,
    get_temp_path,
)
from bear_dereth.config.quick_settings import SimpleSettingsManager
from bear_dereth.config.settings_manager import BearSettings, SettingsManager, StorageChoices

__all__ = [
    "BaseSettingHandler",
    "BearSettings",
    "ConfigManager",
    "DirectoryManager",
    "SettingsManager",
    "SimpleSettingsManager",
    "StorageChoices",
    "TableWrapper",
    "clear_temp_directory",
    "get_cache_path",
    "get_config_path",
    "get_local_config_path",
    "get_settings_path",
    "get_temp_path",
]
