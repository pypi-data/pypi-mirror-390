"""A buffer handler for logging output."""

from __future__ import annotations

from io import StringIO
from typing import IO, TYPE_CHECKING, Any, ClassVar, TextIO

from rich.console import Console

from bear_dereth.di import Provide, inject
from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.config import ConsoleOptions, Container, LoggerConfig
from bear_dereth.logger.formatters.template_formatter import TemplateFormatter
from bear_dereth.logger.protocols.handler import Handler

if TYPE_CHECKING:
    from collections.abc import Callable

    from bear_dereth.di import Provider
    from bear_dereth.logger.records.record import LoggerRecord


class BufferHandler[Handler_Type: TextIO | IO | StringIO](Handler):
    """A buffer handler that outputs messages to a buffer."""

    default_caller: ClassVar[type[Console]] = Console
    caller_attr: ClassVar[str] = "print"

    @inject
    def __init__(
        self,
        *,
        name: str = "console",
        error_callback: Callable[..., Any] = Provide[Container.error_callback],
        root_level: Callable[[], LogLevel] = Provide[Container.root_level],
        console_options: ConsoleOptions = Provide[Container.console_options],
        config: LoggerConfig = Provide[Container.config],
        file: Handler_Type | None = None,
        level: LogLevel | str | int = LogLevel.DEBUG,
        caller: Console | None = None,
        fmt: str | None = None,
        formatter: TemplateFormatter | None = None,
    ) -> None:
        """A constructor for the Handler protocol.

        Args:
            name: Handler name for identification
            error_callback: Callback for handling errors (from DI)
            root_level: Root logging level provider (from DI)
            console_options: Console options for Rich (from DI)
            config: Logger configuration (from DI)
            file: The buffer to write log messages to
            level: Minimum logging level for this handler
            caller: The Rich Console instance to use
            fmt: The format string for log messages
            formatter: The formatter instance for log messages
        """
        self.get_level: Callable[..., LogLevel] = root_level
        self.level = LogLevel.get(level, default=self.get_level())

        super().__init__()
        self.name = name
        self.file = file or StringIO()
        self.error_callback: Callable[..., Any] = error_callback
        self.console_options: ConsoleOptions | Provider = console_options
        self.kwargs = {**console_options.model_dump(exclude_none=True)}
        self.caller = caller or self.factory()
        self.formatter: TemplateFormatter = (
            formatter if formatter is not None else TemplateFormatter(fmt=(fmt or config.console.fmt))
        )

    def emit(self, record: LoggerRecord, **kwargs) -> None:
        """Emit a log message with the given style and arguments.

        Args:
            record: The LoggerRecord to emit
            **kwargs: Additional keyword arguments for Rich formatting
        """
        if self.caller and self.should_emit(record.level):
            try:
                formatted_msg: str = self.formatter.format(record, **kwargs)
                self.output_func(formatted_msg, style=record.style, **kwargs)
            except Exception as e:
                self.error_callback("Error during BufferHandler emit", error=e, name=self.name or "buffer_handler")

    def flush(self) -> None:
        """Flush the buffer if it's a StringIO."""
        if isinstance(self.file, StringIO):
            self.file.flush()

    def close(self) -> None:
        """Do nothing with console handler close."""
        if self.file is None:
            return
        if isinstance(self.file, StringIO) and not self.file.closed:
            self.file.close()
