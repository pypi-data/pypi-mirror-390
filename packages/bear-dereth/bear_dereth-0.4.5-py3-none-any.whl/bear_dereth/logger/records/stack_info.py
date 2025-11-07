"""BasePrinter protocol definition."""

from __future__ import annotations

from functools import lru_cache
import inspect
from pathlib import Path
import sys
from sys import exc_info
import traceback
from types import FrameType, TracebackType
from typing import Final, NamedTuple

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer

IGNORED: Final[set[str]] = {
    "_wrapped_print",
    "on_error_callback",
    "emit",
    "_emit_to_handlers",
    "from_current_stack",
    "_make_record",
}
"""A set containing function names to ignore when capturing stack info."""

EXEC_INFO = tuple[type[BaseException], BaseException, TracebackType] | tuple[None, None, None]
"""Type alias for exception info tuples."""


class ModulePathInfo(NamedTuple):
    """A named tuple to hold module path information."""

    module_path: str
    project_root: Path


class StackInfo(BaseModel):
    """A model to hold stack information."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    path: Path
    caller_function: str
    line_number: int
    code_context: list[str] | None
    index: int | None
    stack_value: int | None = None
    exec_frame: str | None = None  # This allows the exec_frame to be validated back from str
    exception: Exception | None = Field(default=None, repr=False)

    @field_serializer("exec_frame")
    def serialize_exec_frame(self, v: FrameType | None) -> str | None:
        """Serialize exec_frame to a string representation."""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        return f"Frame({v.f_code.co_name} at {v.f_code.co_filename}:{v.f_lineno})"

    @field_serializer("exception")
    def serialize_exception(self, v: Exception | None) -> str | None:
        """Serialize exception to its string representation."""
        if v is None:
            return None
        return str(v)

    @computed_field
    @property
    def filename(self) -> str:
        """Just the filename without path - perfect for log formatting."""
        return self.path.name

    @computed_field
    @property
    def fullpath(self) -> str:
        """Full file path as string - useful for detailed logging."""
        return str(self.path)

    @computed_field
    @property
    def relative_path(self) -> str:
        """Get the file path relative to the current working directory."""
        proj_root: ModulePathInfo | None = get_module_path(str(self.path))
        try:
            root: Path = proj_root.project_root if proj_root is not None else Path.cwd()
            relative_path: Path = self.path.relative_to(root)
            return str(relative_path)
        except ValueError:
            return str(self.path)

    @computed_field
    @property
    def python_path(self) -> str:
        """Convert the file path to a Python module path."""
        mod_path: ModulePathInfo | None = get_module_path(str(self.path))
        return mod_path.module_path if mod_path is not None else "<unknown>"

    @computed_field
    @property
    def code_line(self) -> str:
        """The actual code line if available, otherwise '<unknown>'."""
        if self.code_context and self.index is not None:
            return self.code_context[self.index].strip()
        return "<unknown>"

    @computed_field
    @property
    def location(self) -> str:
        """Formatted location string: filename:line_number."""
        return f"{self.filename}:{self.line_number}"

    @computed_field
    @property
    def full_location(self) -> str:
        """Formatted location with function: filename:line_number@function."""
        return f"{self.filename}:{self.line_number}@{self.caller_function}"

    @computed_field
    @property
    def exception_class(self) -> str | None:
        """Get the exception class name if an exception is present."""
        if self.exception is not None:
            return type(self.exception).__name__
        return None

    @computed_field
    @property
    def exception_details(self) -> str | None:
        """Get formatted exception details if an exception is present."""
        if self.exception is not None:
            return format_exception(self.exception)
        return None

    @classmethod
    def from_current_stack(cls, ignored_functions: set[str] | None = None) -> StackInfo:
        """Create a StackInfo instance from the current stack, ignoring specified functions."""
        ignored: set[str] = set(IGNORED)
        if ignored_functions is not None:
            ignored: set[str] = ignored.union(ignored_functions)

        exc = ExceptionIntrospection()
        stack: list[inspect.FrameInfo] = inspect.stack()
        stack_value = 0
        while stack_value < len(stack) and stack[stack_value].function in ignored:
            stack_value += 1

        caller_frame: inspect.FrameInfo = stack[stack_value]

        return cls(
            caller_function=caller_frame.function,
            path=Path(caller_frame.filename).resolve(),
            line_number=caller_frame.lineno,
            code_context=caller_frame.code_context,
            index=caller_frame.index,
            stack_value=stack_value,
            exec_frame=f"Frame({caller_frame.function} at {caller_frame.filename}:{caller_frame.lineno})",
            exception=exc.exception,
        )


def format_exception(e: Exception, max_length: int = 2000) -> str:
    """Format exception details including stack trace if enabled.

    Args:
        exception(Exception): The exception to format
        max_length(int): Maximum length of the formatted exception string
    Returns:
        A formatted string with exception details
    """
    full_trace: str = "".join(traceback.format_exception(type(e), e, e.__traceback__))

    if len(full_trace) > max_length:
        truncated: str = full_trace[:max_length]
        return f"{truncated}\n... (truncated at {max_length} chars)"
    return full_trace.rstrip()


@lru_cache(maxsize=256)
def get_module_path(filepath: str) -> ModulePathInfo | None:
    """Try to build a Python module path from a filepath.

    Args:
        filepath: The file path to convert.

    Returns:
        The Python module path, or None if it cannot be determined.
    """
    parts: list[str] = []
    path = Path(filepath)
    search_string = "__init__.py"
    current: Path = path.parent

    while (current / search_string).exists():
        parts.insert(0, current.name)
        current = current.parent
    parts.append(path.stem)

    module_path: str | None = ".".join(parts) if parts else None
    project_root: Path | None = current if module_path is not None else None
    if module_path is None or project_root is None:
        return None
    return ModulePathInfo(module_path=module_path, project_root=project_root)


class ExceptionIntrospection:
    """A class to introspect the current exception and its frame."""

    def __init__(self, frame_n: int = 2) -> None:
        """Initialize FrameIntrospection with current exception info."""
        self.exception_info: EXEC_INFO = exc_info()
        self.type: type[BaseException] | None = self.exception_info[0]
        self.value: Exception | None = self.exception_info[1]  # type: ignore[assignment]
        self.traceback: TracebackType | None = self.exception_info[2]
        self.frame_n: int = frame_n
        self.frame: FrameType | None = None
        if self.traceback is not None and hasattr(sys, "_getframe"):
            self.frame = sys._getframe()  # type: ignore[attr-defined]
        else:
            self.frame = get_frame_fallback(self.frame_n)

    @property
    def exception(self) -> Exception | None:
        """Get the current exception value."""
        return self.value


def get_frame_fallback(n: int) -> FrameType | None:
    """Fallback implementation to get the frame n levels up the stack."""
    try:
        raise Exception  # noqa: TRY301 TRY002
    except Exception:
        frame: TracebackType | FrameType | None = exc_info()[2]
        if frame is not None:
            frame = frame.tb_frame.f_back
        for _ in range(n):
            if frame is not None:
                frame = frame.f_back
        return frame
