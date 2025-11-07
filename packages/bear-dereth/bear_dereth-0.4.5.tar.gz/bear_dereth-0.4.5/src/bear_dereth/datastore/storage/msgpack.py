"""MessagePack storage backend for the datastore.

Provides binary MessagePack file storage using the unified data format.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bear_dereth.datastore.storage._base_storage import Storage
from bear_dereth.datastore.unified_data import UnifiedDataFormat
from bear_dereth.files.helpers import touch
from bear_dereth.files.msgpack.file_handler import MsgPackFileHandler

if TYPE_CHECKING:
    from pathlib import Path


class MsgPackStorage(Storage):
    """A MessagePack binary file storage backend using the unified data format."""

    def __init__(self, file: str | Path, file_mode: str = "r+b") -> None:
        """Initialize the MessagePack storage.

        Args:
            file: Path to the MessagePack file
            file_mode: File mode for opening (default: "r+b" for binary read/write)
        """
        super().__init__()
        self.file: Path = touch(file, mkdir=True, create_file=True)
        self.handler = MsgPackFileHandler(file=self.file, mode=file_mode)

    def read(self) -> UnifiedDataFormat | None:
        """Read data from the MessagePack file.

        Returns:
            UnifiedDataFormat instance or None if empty.

        Note:
            Extra fields in records not matching the schema columns are filtered out.
        """
        try:
            data: Any = self.handler.read()
            if data is None:
                return None
            tables: dict[str, dict[str, Any]] = data.get("tables", {})
            for table_data in tables.values():
                columns: list[dict[str, Any]] = table_data.get("columns", [])
                valid_columns: set[str] = {col["name"] for col in columns}
                records: list[dict[str, Any]] = table_data.get("records", [])
                filtered_records: list[dict[str, Any]] = []
                for record in records:
                    filtered_record: dict[str, Any] = {k: v for k, v in record.items() if k in valid_columns}
                    filtered_records.append(filtered_record)
                table_data["records"] = filtered_records
            return UnifiedDataFormat.model_validate(data)
        except Exception:
            return None

    def write(self, data: UnifiedDataFormat) -> None:
        """Write data to the MessagePack file, replacing existing content.

        Args:
            data: UnifiedDataFormat instance to write.

        Note:
            Records are filtered to only include fields matching the schema columns.
        """
        data_dict: dict[str, Any] = data.model_dump(exclude_none=True)
        tables: dict[str, dict[str, Any]] = data_dict.get("tables", {})
        for table_data in tables.values():
            columns: list[dict[str, Any]] = table_data.get("columns", [])
            valid_columns: set[str] = {col["name"] for col in columns}
            records: list[dict[str, Any]] = table_data.get("records", [])
            filtered_records: list[dict[str, Any]] = []
            for record in records:
                filtered_record: dict[str, Any] = {k: v for k, v in record.items() if k in valid_columns}
                filtered_records.append(filtered_record)
            table_data["records"] = filtered_records
        self.handler.write(data_dict)

    def close(self) -> None:
        """Close all file handles."""
        if self.closed:
            return
        self.handler.close()

    @property
    def closed(self) -> bool:
        """Check if all file handles are closed."""
        return self.handler.closed


__all__ = ["MsgPackStorage"]
