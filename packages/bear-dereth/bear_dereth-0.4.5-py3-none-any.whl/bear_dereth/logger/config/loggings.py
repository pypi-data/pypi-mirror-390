"""Logger configuration and theming using Pydantic and Rich."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from bear_epoch_time.constants import DT_FORMAT_WITH_SECONDS
from lazy_bear import LazyLoader
from pydantic import BaseModel, Field

from bear_dereth.constants import Megabytes
from bear_dereth.logger.common.consts import EXCEPTION_FMT, MEDIUM_FMT, MSG_ONLY_FMT
from bear_dereth.logger.common.log_level import LogLevelModel
from bear_dereth.models.type_fields import PathModel

if TYPE_CHECKING:
    import queue as _queue
else:
    _queue = LazyLoader("queue")


class RootLoggerConfig(BaseModel):
    """A Pydantic model representing the root logger configuration."""

    model_config = {"extra": "forbid", "frozen": True}

    disable: bool = False
    fmt: str = MSG_ONLY_FMT
    level: LogLevelModel = LogLevelModel().set("DEBUG")
    overrides: dict[str, Any] = Field(default_factory=dict)


class FileConfig(BaseModel):
    """A Pydantic model representing a file handler configuration."""

    model_config = {"extra": "forbid", "frozen": True}

    disable: bool = True
    max_size: int = Megabytes(10)
    rotations: int = 5
    path: PathModel = PathModel().set(Path("logs/app.log"))
    mode: str = "a"
    encoding: str = "utf-8"
    fmt: str = MEDIUM_FMT
    overrides: dict[str, Any] = Field(default_factory=dict)
    respect_handler_level: bool = True


class ConsoleHandlerConfig(BaseModel):
    """A Pydantic model representing a console handler configuration."""

    disable: bool = False
    fmt: str = MSG_ONLY_FMT
    overrides: dict[str, Any] = Field(default_factory=dict)
    respect_handler_level: bool = True


class QueueConfig(BaseModel):
    """A Pydantic model representing a queue listener configuration."""

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True, "frozen": True}

    disable: bool = True
    max_queue_size: int = 1000
    worker_count: int = 2
    flush_interval: float = 0.5  # seconds
    queue: _queue.Queue = Field(default_factory=_queue.Queue, exclude=True)
    respect_handler_level: bool = True


# TODO: Not sure we still need this here and in all of the above configs?
class FormatterConfig(BaseModel):
    """A Pydantic model representing formatter configuration."""

    model_config = {"extra": "forbid", "frozen": True}

    console_fmt: str = MSG_ONLY_FMT
    file_fmt: str = MEDIUM_FMT
    json_fmt: str | None = None
    exception_fmt: str = EXCEPTION_FMT

    datefmt: str = DT_FORMAT_WITH_SECONDS
    use_local_timezone: bool = True
    include_microseconds: bool = False
    iso_format: bool = False  # Use ISO 8601 format instead of custom datefmt

    disable: bool = False
    include_stack_trace: bool = True  # For exceptions
    max_exception_length: int = 2000  # Truncate very long exception traces
    overrides: dict[str, Any] = Field(default_factory=dict)


__all__ = ["ConsoleHandlerConfig", "FileConfig", "FormatterConfig", "QueueConfig", "RootLoggerConfig"]
