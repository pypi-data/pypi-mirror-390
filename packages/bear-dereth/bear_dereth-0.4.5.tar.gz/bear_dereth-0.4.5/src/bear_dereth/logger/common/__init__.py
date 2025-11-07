"""A simple logger setup."""

from .consts import FILE_MODE, BaseOutput, CallableOrFile, ExtraStyle, HandlerModes
from .log_level import LogLevel

__all__ = [
    "FILE_MODE",
    "BaseOutput",
    "CallableOrFile",
    "ExtraStyle",
    "HandlerModes",
    "LogLevel",
]
