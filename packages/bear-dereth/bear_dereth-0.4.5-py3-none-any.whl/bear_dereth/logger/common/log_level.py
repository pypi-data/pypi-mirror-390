"""This is some terrible sinning that should not exist, don't look at it. It doesn't exist if you don't look at it."""

from __future__ import annotations

from typing import Any, Literal, Self

from funcy_bear.rich_enums import IntValue as LogValue, RichIntEnum
from pydantic import ConfigDict, Field, RootModel, SerializerFunctionWrapHandler, field_serializer, field_validator

EXCEPTION: Literal[50] = 50
FAILURE: Literal[45] = 45
ERROR: Literal[40] = 40
WARNING: Literal[30] = 30
WARN: Literal[30] = WARNING
INFO: Literal[20] = 20
SUCCESS: Literal[15] = 15
DEBUG: Literal[10] = 10
VERBOSE: Literal[5] = 5
NOTSET: Literal[0] = 0


class LogLevel(RichIntEnum):
    """Enumeration for logging levels."""

    NOTSET = LogValue(NOTSET, "NOTSET")
    VERBOSE = LogValue(VERBOSE, "VERBOSE")
    DEBUG = LogValue(DEBUG, "DEBUG")
    INFO = LogValue(INFO, "INFO")
    WARNING = LogValue(WARNING, "WARNING")
    ERROR = LogValue(ERROR, "ERROR")
    FAILURE = LogValue(FAILURE, "FAILURE")
    SUCCESS = LogValue(SUCCESS, "SUCCESS")
    EXCEPTION = LogValue(EXCEPTION, "EXCEPTION")
    INVALID_LEVEL = LogValue(999, "INVALID_LEVEL")

    @classmethod
    def level_to_name(cls, level: int | str | Self) -> str:
        """Get the name of a logging level."""
        return LogLevel.get(level, default=LogLevel.INVALID_LEVEL).name

    @classmethod
    def name_to_level(cls, name: str | Self) -> int:
        """Get the numeric value of a logging level by its name."""
        return LogLevel.get(name, default=LogLevel.INVALID_LEVEL).value


class LogLevelModel(RootModel[LogLevel]):
    """A model to handle log levels."""

    model_config = ConfigDict(frozen=False, validate_by_name=True)
    root: LogLevel = Field(default=LogLevel.INFO)

    def set(self, v: str | int | LogLevel) -> Self:
        """Set a new LogLevel."""
        self.root = self.convert_level(v)
        return self

    @property
    def level(self) -> LogLevel:
        """Get the current LogLevel."""
        return self.root

    @level.setter
    def level(self, new_level: str | int | LogLevel) -> None:
        """Set a new LogLevel."""
        self.root = LogLevel.get(new_level, self.root)

    @field_validator("root", mode="before")
    @classmethod
    def convert_level(cls, v: Any) -> Any:
        """Convert a string or int to LogLevel."""
        if isinstance(v, (str | int)):
            return LogLevel.get(v)
        return v

    @field_serializer("root", mode="wrap")
    def serialize_level(self, value: Any, nxt: SerializerFunctionWrapHandler) -> str:
        """Serialize the LogLevel to a string."""
        level_value: Any = nxt(value)
        return str(level_value)

    def __str__(self) -> str:
        return str(self.root)

    def __repr__(self) -> str:
        return repr(self.root)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.root, name)

    def __call__(self, *_: Any, **__: Any) -> LogLevel:
        """Allow the model instance to be called to get the LogLevel."""
        return self.root
