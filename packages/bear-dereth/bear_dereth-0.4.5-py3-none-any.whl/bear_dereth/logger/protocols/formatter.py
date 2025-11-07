"""Formatter protocol definition for the logger system."""

from typing import Any, Protocol, Self, overload

from funcy_bear.api import LitFalse, LitTrue, has_exception

from bear_dereth.logger.config.loggings import FormatterConfig
from bear_dereth.logger.records import LoggerRecord
from bear_dereth.logger.records.fmt import FormatCompiler
from bear_dereth.logger.records.time_helper import TimeHelper


class Formatter(Protocol):
    """A protocol for log message formatters.

    Formatters are responsible for transforming raw log data into formatted strings
    that can be consumed by handlers for output.
    """

    name: str = ""
    fmt: str
    datefmt: str
    exec_fmt: str
    time_helper: TimeHelper
    fmt_config: FormatterConfig
    _tmpl: FormatCompiler
    _exec_tmpl: FormatCompiler

    tz: str

    def __new__(cls, *args, **kwargs) -> Self:  # noqa: ARG004
        """Create a new instance of the formatter."""
        new: Self = super().__new__(cls)
        new.name = cls.__name__
        return new

    def __init__(
        self,
        config: FormatterConfig,
        fmt: str,
        datefmt: str,
        exec_fmt: str,
    ) -> None:
        """Initialize the formatter with an optional name and format templates.

        Args:
            config: Formatter configuration instance
            fmt: Format template string
            datefmt: Optional date format string
            exec_fmt: Optional separate template for exception messages (falls back to fmt if not provided)
        """
        self.fmt: str = fmt
        self.datefmt: str = datefmt
        self.time_helper: TimeHelper = TimeHelper()  # TODO: Ensure all date/time formatting are forwarded as per config
        self.exec_fmt: str = exec_fmt
        self.fmt_config: FormatterConfig = config
        self._tmpl = FormatCompiler(self.fmt)
        self._exec_tmpl = FormatCompiler(self.exec_fmt)
        self.tz = str(self.time_helper.tz)  # Not likely to change, so just store as str

    @overload
    def format(self, record: LoggerRecord, as_dict: LitTrue, **kwargs) -> dict: ...
    @overload
    def format(self, record: LoggerRecord, as_dict: LitFalse = False, **kwargs) -> str: ...

    def format(self, record: LoggerRecord, as_dict: bool = False, **kwargs) -> str | dict:
        """Format a log message into a string.

        Args:
            record(LoggerRecord): The log record to format
            **kwargs: Additional context data for formatting

        Returns:
            A formatted string ready for output by a handler
        """
        subs: dict[str, Any] = self._to_dict(record, **kwargs)
        if as_dict:
            return subs
        if has_exception(record.stack_info.exception):
            return self._exec_tmpl.compile(**subs)
        return self._tmpl.compile(**subs)

    def _to_dict(self, record: LoggerRecord, **kwargs) -> dict[str, Any]:
        """Create a dictionary of log record attributes for formatting.

        Args:
            record(LoggerRecord): The log record to extract data from
            **kwargs: Additional context data to include
        Returns:
            A dictionary of log record attributes and additional context
        """
        timestamp, date, time = self.time_helper.get_all(record.timestamp)
        return {
            "timestamp": timestamp,
            "time": time,
            "date": date,
            "tz": self.tz,
            **record.model_dump(),
            **kwargs,
        }
