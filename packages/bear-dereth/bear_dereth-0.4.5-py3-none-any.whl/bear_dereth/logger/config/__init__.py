"""A set of logger configuration components and utilities."""

from bear_dereth.logger.config._get import LoggerConfig
from bear_dereth.logger.config.console import ConsoleOptions, CustomTheme
from bear_dereth.logger.config.di import Container, get_container
from bear_dereth.logger.config.loggings import (
    ConsoleHandlerConfig,
    FileConfig,
    FormatterConfig,
    QueueConfig,
    RootLoggerConfig,
)

__all__ = [
    "ConsoleHandlerConfig",
    "ConsoleOptions",
    "Container",
    "CustomTheme",
    "FileConfig",
    "FormatterConfig",
    "LoggerConfig",
    "QueueConfig",
    "RootLoggerConfig",
    "get_container",
]
