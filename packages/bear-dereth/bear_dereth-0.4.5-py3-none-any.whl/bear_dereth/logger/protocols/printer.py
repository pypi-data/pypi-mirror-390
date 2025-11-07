"""BasePrinter protocol definition."""

from typing import IO, Any, TextIO

from funcy_bear.type_stuffs.hint import TypeHint

from bear_dereth.logger.common.error_handler import ErrorHandler
from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.config.console import CustomTheme, LoggerConfig
from bear_dereth.logger.protocols import BaseHandlerManager, Handler, TypeLogger


class BasePrinter[T: TextIO | IO](BaseHandlerManager):
    """A protocol for a base printer with config, theme, and user API."""

    name: str | None
    config: LoggerConfig
    level: LogLevel
    theme: CustomTheme
    handlers: list[Handler[Any]]
    start_no_handlers: bool

    def __init__(
        self,
        name: str | None = None,
        config: LoggerConfig | None = None,
        custom_theme: CustomTheme | None = None,  # noqa: ARG002
        file: T | None = None,  # noqa: ARG002
        level: int | str | LogLevel = LogLevel.DEBUG,
        error_callback: ErrorHandler | None = None,
        start_no_handlers: bool = False,
    ) -> None:
        """A constructor for the BasePrinter protocol."""
        self.name = name
        self.config = config or LoggerConfig()
        self.level = LogLevel.get(level, default=LogLevel.DEBUG)
        self.start_no_handlers = start_no_handlers
        self.on_error_callback: ErrorHandler = error_callback or ErrorHandler()

    def get_level(self) -> LogLevel:
        """Get the current logging level."""
        return self.level

    def set_level(self, level: str | int | LogLevel) -> None:
        """Set the current logging level."""
        self.level = LogLevel.get(level, self.level)

    def print(self, msg: object, style: str | None = None, **kwargs) -> None:
        """A method to print a message with a specific style directly to the console."""

    def log(self, msg: object, *args, **kwargs) -> None:
        """A method to log a message via console.log()."""


class LoggerPrinter(BasePrinter, TypeHint(TypeLogger)):
    """A combined protocol for a logger printer with TypeLogger and BasePrinter features."""
