"""Module providing a WrappedPath class for enhanced Path handling and metadata extraction."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

from lazy_bear import LazyLoader
from pydantic import BaseModel, computed_field, field_validator

from bear_dereth.constants import GIGABYTES, KILOBYTES, MEGABYTES

if TYPE_CHECKING:
    from os import stat_result

    from bear_epoch_time import EpochTimestamp

    from bear_dereth.data_structs.queuestuffs import SimpooQueue
    from bear_dereth.files.helpers import get_file_hash
    from bear_dereth.platform_utils import OS, get_platform
else:
    EpochTimestamp = LazyLoader("bear_epoch_time").to("EpochTimestamp")
    SimpooQueue = LazyLoader("bear_dereth.data_structs.queuestuffs").to("SimpooQueue")
    get_file_hash = LazyLoader("bear_dereth.files.helpers").to("get_file_hash")
    OS, get_platform = LazyLoader("bear_dereth.platform_utils").to_many("OS", "get_platform")


INVALID_METRIC = -1


def get_parents(path: Path) -> dict[str, WrappedPath]:
    """Get all parent directories of the given path as a dictionary."""

    def parse_parents(path: Path) -> dict[str, WrappedPath]:
        """Get immediate parent with its own parent chain."""
        if path.parent == path:
            return {}
        immediate_parent = WrappedPath(path=path.parent)
        return {str(path.parent): immediate_parent}

    queue: SimpooQueue[Path] = SimpooQueue()
    current_path: Path = path.parent
    while current_path != current_path.parent:
        queue.enqueue(current_path)
        current_path = current_path.parent
    parents_dict: dict[str, WrappedPath] = {}
    while queue:
        p: Path = queue.dequeue()
        parents_dict = {**parse_parents(p), **parents_dict}
    return parents_dict


class WrappedPath(BaseModel):
    """A class to wrap a Path object and provide additional attributes and methods.

    This for easily serializing Path objects and getting useful metadata for external use.
    """

    path: Path

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v: Any) -> Path:
        """Validate and convert the input to a Path object."""
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            return v.expanduser().resolve()
        raise TypeError(f"Path must be a str or Path object, got {type(v)}")

    @computed_field
    @property
    def name(self) -> str:
        """The name of the file or directory like 'file.txt'."""
        return self.path.name

    @computed_field
    @property
    def suffix(self) -> str:
        """The file extension, if any like '.txt'."""
        return self.path.suffix

    @computed_field
    @property
    def stem(self) -> str:
        """The name of the file without the suffix, like 'file'."""
        return self.path.stem

    @computed_field
    @property
    def absolute(self) -> Path:
        """The absolute path of the file or directory."""
        return self.path.resolve()

    @computed_field
    @property
    def is_absolute(self) -> bool:
        """Whether the path is absolute."""
        return self.path.is_absolute()

    @computed_field
    @property
    def exists(self) -> bool:
        """Whether the path exists."""
        return self.path.exists()

    @computed_field
    @property
    def is_dir(self) -> bool:
        """Whether the path is a directory."""
        return self.path.is_dir()

    @computed_field
    @property
    def is_file(self) -> bool:
        """Whether the path is a file."""
        return self.path.is_file()

    @computed_field
    @property
    def is_symlink(self) -> bool:
        """Whether the path is a symbolic link."""
        return self.path.is_symlink()

    @computed_field
    @property
    def is_mount(self) -> bool:
        """Whether the path is a mount point."""
        return self.path.is_mount()

    @computed_field
    @property
    def parts(self) -> list[str]:
        """The parts of the path as a list."""
        return list(self.path.parts)

    @computed_field
    @property
    def as_uri(self) -> str:
        """The URI representation of the path."""
        return self.path.as_uri()

    @cached_property
    def stat(self) -> stat_result | None:
        """Get the stat result of the path."""
        return self.path.stat() if self.exists else None

    @cached_property
    def _is_binary(self) -> bool:
        """Check if the file is binary by attempting to read it as text."""
        if not self.is_file or not self.exists:
            return False
        try:
            self.path.read_text(encoding="utf-8")
            return False
        except UnicodeDecodeError:
            return True

    @computed_field
    @property
    def is_binary(self) -> bool:
        """Whether the file is binary."""
        return self._is_binary

    @cached_property
    def _lines(self) -> int:
        """Read the lines of the file if it's a text file."""
        if not self.is_file or not self.exists or self.is_binary:
            return INVALID_METRIC
        try:
            return len(self.path.read_text(encoding="utf-8").splitlines())
        except Exception:
            return INVALID_METRIC

    @computed_field
    @property
    def lines(self) -> int:
        """The number of lines in the file if it's a text file."""
        return self._lines

    @computed_field
    @property
    def modified(self) -> int:
        """The last modified time of the file or directory."""
        if self.stat is None:
            return INVALID_METRIC
        return int((self.stat.st_mtime * 1000) if self.exists else 0.0)

    @computed_field
    @property
    def modified_str(self) -> str:
        """The last modified time as a string."""
        modified_ts = EpochTimestamp(self.modified)
        return modified_ts.to_string() if self.modified != INVALID_METRIC else ""

    @cached_property
    def _created(self) -> int:
        """Get the file creation time as a timestamp."""
        platform: OS = get_platform()
        if platform is OS.DARWIN and hasattr(self.stat, "st_birthtime"):
            return int(getattr(self.stat, "st_birthtime", INVALID_METRIC) * 1000)
        if platform is OS.WINDOWS and self.stat is not None:
            return int(self.stat.st_ctime * 1000)
        return int(self.stat.st_mtime * 1000) if self.stat is not None else INVALID_METRIC

    @computed_field
    @property
    def created(self) -> int:
        """The creation time of the file or directory."""
        return self._created

    @computed_field
    @property
    def created_str(self) -> str:
        """The creation time as a string."""
        created_ts = EpochTimestamp(self.created)
        return created_ts.to_string() if self.created != INVALID_METRIC else ""

    @computed_field
    @property
    def file_size(self) -> int:
        """The size of the file in bytes."""
        if self.stat is None:
            return INVALID_METRIC
        return self.stat.st_size if self.is_file else INVALID_METRIC

    @computed_field
    @property
    def file_size_str(self) -> str:
        """The size of the file in a human-readable format."""
        if self.file_size == INVALID_METRIC:
            return "N/A"
        if self.file_size >= GIGABYTES:
            return f"{(self.file_size / GIGABYTES):.2f} GB"
        if self.file_size >= MEGABYTES:
            return f"{(self.file_size / MEGABYTES):.2f} MB"
        if self.file_size >= KILOBYTES:
            return f"{(self.file_size / KILOBYTES):.2f} KB"
        return f"{self.file_size} bytes"

    @computed_field
    @property
    def file_hash(self) -> str:
        """Get the SHA256 hash of the file."""
        if not self.is_file or not self.exists:
            return ""
        return get_file_hash(self.path)

    @computed_field
    @property
    def parent(self) -> dict[str, WrappedPath]:
        """Recursive parent directories."""
        return get_parents(self.path)

    def __str__(self) -> str:
        """Return a string representation of the WrappedPath instance."""
        return self.model_dump_json(indent=4, exclude_none=True)

    def __repr__(self) -> str:
        """Return a detailed string representation of the WrappedPath instance."""
        return f"WrappedPath(path={self.path!r})"


if __name__ == "__main__":
    wp = WrappedPath(path=__file__)  # pyright: ignore[reportArgumentType]

    print(wp.model_dump_json(indent=4, exclude={"parent"}))
