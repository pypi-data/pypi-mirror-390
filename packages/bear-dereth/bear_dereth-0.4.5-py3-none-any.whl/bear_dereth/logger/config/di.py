"""A dependency injection container for logger configuration components."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from bear_dereth.config import ConfigManager
from bear_dereth.di import DeclarativeContainer, Provide, Provider, Resource, Singleton
from bear_dereth.logger.common.error_handler import ErrorHandler
from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.config._get import LoggerConfig
from bear_dereth.logger.config.console import ConsoleOptions, CustomTheme

if TYPE_CHECKING:
    from collections.abc import Callable


def get_custom_theme(config: LoggerConfig) -> CustomTheme:
    """Get a custom theme from the logger configuration."""
    return CustomTheme.from_config(config)


def get_console_options(custom_theme: CustomTheme, config: LoggerConfig) -> ConsoleOptions:
    """Get console options with the custom theme applied and root overrides."""
    options = ConsoleOptions(theme=custom_theme)
    return options.model_copy(update=config.root.overrides)


def get_root_level(default: str = "DEBUG") -> Callable[[], LogLevel]:
    """Default root level getter."""

    def debug_level() -> LogLevel:
        return LogLevel.get(default, LogLevel.DEBUG)

    return debug_level


def get_config_manager(program_name: str = "logger", env: str | None = None) -> ConfigManager[LoggerConfig]:
    """Get the configuration manager for the logger.

    Args:
        program_name: The name of the program for configuration purposes.
        env: The environment to use for configuration. If None, defaults to the BEAR_DERETH_ENV environment variable or "prod".

    Returns:
        A ConfigManager instance for LoggerConfig.
    """
    return ConfigManager(
        LoggerConfig,
        program_name=program_name,
        env=os.environ.get("BEAR_DERETH_ENV", "prod") if env is None else env,
    )


def get_default_config(config_manager: ConfigManager) -> LoggerConfig:
    """Get the default logger configuration."""
    return config_manager.config


class Container(DeclarativeContainer):
    """Dependency injection container for logger components."""

    root_level: Resource[Callable[[], LogLevel]] = Resource(get_root_level)
    error_callback: Singleton[ErrorHandler] = Singleton(ErrorHandler)
    config_manager: Singleton[ConfigManager[LoggerConfig]] = Singleton(get_config_manager, program_name="logger")
    config: Resource[LoggerConfig] = Resource(get_default_config, config_manager=config_manager)
    custom_theme: Resource[CustomTheme] = Resource(get_custom_theme, config=config)
    console_options: Resource[ConsoleOptions] = Resource(get_console_options, custom_theme=custom_theme, config=config)


def get_container(provide: Provider = Provide) -> Container:
    """Get the DI container

    Args:
        provide: The provider to use for DI.

    Returns:
        An instance of the Container.
    """
    container = Container()
    provide.set_container(Container)
    return container
