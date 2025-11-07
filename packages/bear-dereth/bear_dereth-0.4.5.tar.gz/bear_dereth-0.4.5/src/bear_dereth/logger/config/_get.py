from pydantic import BaseModel

from .loggings import (
    ConsoleHandlerConfig,
    FileConfig,
    FormatterConfig,
    QueueConfig,
    RootLoggerConfig,
)
from .theme import LoggerTheme


class LoggerConfig(BaseModel):
    """A Pydantic model representing the logger configuration."""

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True}

    root: RootLoggerConfig = RootLoggerConfig()
    console: ConsoleHandlerConfig = ConsoleHandlerConfig()
    file: FileConfig = FileConfig()
    queue: QueueConfig = QueueConfig()
    formatter: FormatterConfig = FormatterConfig()
    theme: LoggerTheme = LoggerTheme()


__all__ = ["LoggerConfig"]
