"""A module defining a protocol for log message handlers."""

from collections.abc import Callable
from typing import IO, Any, ClassVar, Protocol, Self, TextIO

from bear_dereth.files.base_file_handler import BaseFileHandler
from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.records import LoggerRecord


class Handler[Handler_Type: TextIO | IO | BaseFileHandler](Protocol):
    """A protocol for log message handlers."""

    caller_attr: ClassVar[str] = ""
    default_caller: ClassVar[type]
    caller: Any
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    name: str | None
    level: LogLevel
    disabled: bool
    file: Handler_Type | None

    def __init__(self, disabled: bool = False) -> None:
        """A constructor for the Handler protocol."""
        self.disabled = disabled
        self.args = ()
        self.kwargs = {}

    def on_init(self, *args: Any, **kwargs: Any) -> None:
        """A hook for additional initialization if needed."""

    def factory(self) -> Handler_Type:
        """A hook for factory-based initialization if needed."""
        factory: type[Handler_Type] = self._get_factory_type()
        if factory is not None and callable(factory):
            return factory(*self.args, **self.kwargs)
        return None

    @classmethod
    def set_factory_type(cls, factory_type: type[Handler_Type]) -> None:
        """Set the factory type for the handler."""
        cls.default_caller = factory_type

    @classmethod
    def _get_factory_type(cls) -> type[Handler_Type]:
        """Get the factory type if defined."""
        return cls.default_caller

    @classmethod
    def set_mode_attr(cls, value: str) -> None:
        """Set the mode attribute based on the specified mode."""
        cls.caller_attr = value

    @property
    def mode_attr(self) -> str:
        """Get the current mode attribute based on the handler's mode."""
        return self.caller_attr

    @property
    def output_func(self) -> Callable[..., Any]:
        """Get the appropriate output function based on the current mode."""
        get_func: Callable | None = getattr(self.caller, self.mode_attr, None)
        if get_func is None or not callable(get_func):
            raise AttributeError(f"Console has no callable attribute '{self.mode_attr}'")
        return get_func

    def emit(self, record: LoggerRecord, **kwargs) -> None:
        """Emit a log message with the given style and arguments.

        Args:
            record: The LoggerRecord to emit
            **kwargs: Additional keyword arguments for Rich formatting
        """

    def close(self) -> None:
        """Close the handler and clean up any resources."""
        if (
            hasattr(self, "file")
            and self.file
            and hasattr(self.file, "close")
            and not getattr(self.file, "closed", False)
        ):
            self.file.close()

    def flush(self) -> None:
        """Flush any buffered output."""
        if (
            hasattr(self, "file")
            and self.file
            and hasattr(self.file, "flush")
            and not getattr(self.file, "closed", False)
        ):
            self.file.flush()

    def set_level(self, level: str | int | LogLevel) -> None:
        """Set the logging level for this handler."""
        self.level = LogLevel.get(level, default=self.level)

    def should_emit(self, level: LogLevel) -> bool:
        """Check if this handler should emit messages at the given level."""
        return level >= self.level

    def __enter__(self) -> Self:
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit the runtime context related to this object."""
        self.close()
