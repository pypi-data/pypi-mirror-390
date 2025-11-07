"""A collection of common constants for the logging system."""

from collections.abc import Callable
from io import StringIO
from typing import IO, Literal, TextIO

from funcy_bear.files.textio_utility import DEVNULL, stderr, stdout

from bear_dereth.logger.common.log_level import LogLevel

METHOD_NAMES: dict[str, dict[str, LogLevel]] = {
    "debug": {"level": LogLevel.DEBUG},
    "info": {"level": LogLevel.INFO},
    "warning": {"level": LogLevel.WARNING},
    "error": {"level": LogLevel.ERROR},
    "exception": {"level": LogLevel.EXCEPTION},
    "verbose": {"level": LogLevel.VERBOSE},
    "success": {"level": LogLevel.SUCCESS},
    "failure": {"level": LogLevel.FAILURE},
}

HandlerModes = Literal["default", "alt"]
BaseOutput = Literal["stdout", "stderr", "devnull", "string_io"]
ExtraStyle = Literal["flatten", "no_flatten"]
CallableOrFile = Callable[[], TextIO | IO[str] | StringIO] | TextIO | IO[str] | StringIO

WITHOUT_EXCEPTION_NAMES: dict[str, dict[str, LogLevel]] = METHOD_NAMES.copy()
WITHOUT_EXCEPTION_NAMES.pop("exception")

FILE_MODE: dict[BaseOutput, Callable[[], TextIO | IO[str] | StringIO]] = {
    "stdout": stdout,
    "stderr": stderr,
    "devnull": DEVNULL,
    "string_io": StringIO,
}

EXCEPTION_FMT = "$timestamp |$level| Exception in $caller_function ($filename:$line_number): $msg\n$exception_details"
"""Format string for exception log records."""

MEDIUM_FMT = "$timestamp |$level| {$filename|$caller_function|$line_number} $msg"
"""A medium-detail format string for log records."""

SIMPLE_FMT = "$timestamp |$level| $msg"
"""A simple format string for log records."""

MSG_ONLY_FMT = "$msg"
"""A message-only format string for log records."""

__all__ = [
    "EXCEPTION_FMT",
    "FILE_MODE",
    "MEDIUM_FMT",
    "METHOD_NAMES",
    "MSG_ONLY_FMT",
    "SIMPLE_FMT",
    "WITHOUT_EXCEPTION_NAMES",
    "BaseOutput",
    "CallableOrFile",
    "ExtraStyle",
    "HandlerModes",
]
