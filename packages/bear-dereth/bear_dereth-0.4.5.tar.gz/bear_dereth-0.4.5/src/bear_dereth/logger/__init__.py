"""A module providing a Rich-based printer for colorful console output."""

from typing import TYPE_CHECKING

from lazy_bear import LazyLoader

from bear_dereth.logger.config import Container, LoggerConfig, get_container

if TYPE_CHECKING:
    from .basic_logger.basic_logger import BasicLogger
    from .basic_logger.simple_logger import BaseLogger, PrintOnlyLogger, SimpleLogger
    from .common.log_level import LogLevel
    from .handlers import BufferHandler, ConsoleHandler, FileHandler, QueueHandler
    from .rich_printer import BearLogger
else:
    _simple = LazyLoader("bear_dereth.logger.basic_logger.simple_logger")
    BaseLogger = _simple.to("BaseLogger")
    PrintOnlyLogger = _simple.to("PrintOnlyLogger")
    SimpleLogger = _simple.to("SimpleLogger")

    BasicLogger = LazyLoader("bear_dereth.logger.basic_logger.basic_logger").to("BasicLogger")
    BearLogger = LazyLoader("bear_dereth.logger.rich_printer").to("BearLogger")
    LogLevel = LazyLoader("bear_dereth.logger.common.log_level").to("LogLevel")
    BufferHandler = LazyLoader("bear_dereth.logger.handlers.buffer_handler").to("BufferHandler")
    ConsoleHandler = LazyLoader("bear_dereth.logger.handlers.console_handler").to("ConsoleHandler")
    FileHandler = LazyLoader("bear_dereth.logger.handlers.file_handler").to("FileHandler")
    QueueHandler = LazyLoader("bear_dereth.logger.handlers.queue_handler").to("QueueHandler")


__all__ = [
    "BaseLogger",
    "BasicLogger",
    "BearLogger",
    "BufferHandler",
    "ConsoleHandler",
    "Container",
    "FileHandler",
    "LogLevel",
    "LoggerConfig",
    "PrintOnlyLogger",
    "QueueHandler",
    "SimpleLogger",
    "get_container",
]
