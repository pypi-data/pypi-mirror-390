"""TOML storage backend for the datastore.

Provides TOML file storage using the unified data format.
"""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, Any

from funcy_bear.files.text.file_handler import TextFileHandler
import tomlkit
from tomlkit import TOMLDocument
from tomlkit.api import inline_table
from tomlkit.items import Array, InlineTable, Table

from bear_dereth.async_stuffs import lru_cache
from bear_dereth.datastore.record import Record
from bear_dereth.datastore.storage._base_storage import Storage
from bear_dereth.datastore.unified_data import UnifiedDataFormat
from bear_dereth.files.helpers import touch

if TYPE_CHECKING:
    from pathlib import Path

    from tomlkit.items import Array, InlineTable, Table

    from bear_dereth.models.frozen_models import FrozenDict


def get_arr() -> Array:
    """Return a new multiline TOML array."""
    arr: Array = tomlkit.array()
    arr.multiline(multiline=True)
    return arr


@lru_cache(maxsize=128)  # TODO: Make this configurable with BEAR_DERETH_TOML_HEADER_CACHE_SIZE or something like that
def get_cached_header(header_data: FrozenDict) -> Table:
    """Get cached header from TOML storage."""
    header: Table = tomlkit.table()
    for k, v in sorted(header_data.items(), reverse=True):
        header[k] = v
    return header


@lru_cache(maxsize=512)
def get_cached_columns_array(
    columns_frozen: tuple[FrozenDict, ...],
) -> tuple[Array, tuple[str]]:
    """Cache the columns array for a table."""
    arr: Array = get_arr()
    for col_dict in columns_frozen:
        col_table: InlineTable = inline_table()
        for k, v in col_dict.items():
            col_table[k] = v
        arr.append(col_table)
    return arr, tuple(col_dict["name"] for col_dict in columns_frozen)


@lru_cache(maxsize=512)
def get_cached_records_array(records_frozen: tuple[FrozenDict, ...], valid_columns: tuple[str]) -> Array:
    """Cache the records for a table, filtering by valid columns."""
    records_arr: Array = get_arr()
    for record_dict in records_frozen:
        record_table: InlineTable = inline_table()
        filtered_record: dict[str, Any] = {k: v for k, v in record_dict.items() if k in valid_columns}
        for k, v in filtered_record.items():
            record_table[k] = v
        records_arr.append(record_table)
    return records_arr


class TomlStorage(Storage):
    """A TOML file storage backend using the unified data format."""

    def __init__(self, file: str | Path, file_mode: str = "r+", encoding: str = "utf-8") -> None:
        """Initialize TOML storage.

        Args:
            file: Path to the TOML file
            file_mode: File mode for opening (default: "r+" for read/write)
            encoding: Text encoding to use (default: "utf-8")
        """
        super().__init__()
        self.file: Path = touch(file, mkdir=True, create_file=True)
        self.handler = TextFileHandler(self.file, mode=file_mode, encoding=encoding)

    def read(self) -> UnifiedDataFormat | None:
        """Read data from TOML file.

        Returns:
            UnifiedDataFormat instance or None if empty.

        Note:
            Extra fields in records not matching the schema columns are filtered out.
        """
        try:
            text: str = self.handler.read()
            data: dict[str, Any] = tomllib.loads(text)
            unified: UnifiedDataFormat = UnifiedDataFormat.model_validate(data)

            for _, table_data in unified.tables.items():
                valid_columns: set[str] = {col.name for col in table_data.columns}
                filtered_records: list[Record] = []
                for record in table_data.records:
                    filtered_record: dict[str, Any] = {k: v for k, v in record.items() if k in valid_columns}
                    filtered_records.append(Record(**filtered_record))
                table_data.records = filtered_records
            return unified
        except Exception:
            return None

    def write(self, data: UnifiedDataFormat) -> None:
        """Write data to TOML file with pretty inline formatting.

        Args:
            data: UnifiedDataFormat instance to write.
        """
        doc: TOMLDocument = tomlkit.document()
        header: Table = get_cached_header(data.header.frozen_dump())
        doc.add("header", header)

        tables: Table = tomlkit.table()
        for table_name, table_data in data.tables.items():
            table: Table = tomlkit.table()
            frozen_cols: tuple[FrozenDict, ...] = tuple(col.frozen_dump() for col in table_data.columns)
            columns_arr, valid_columns = get_cached_columns_array(frozen_cols)
            table.add("columns", columns_arr)
            table.add("count", table_data.count)
            frozen_recs = tuple(rec.frozen_dump() for rec in table_data.records)
            records_arr: Array = get_cached_records_array(frozen_recs, valid_columns)
            table.add("records", records_arr)
            tables.add(table_name, table)
        doc.add("tables", tables)
        self.handler.write(tomlkit.dumps(doc))

    def close(self) -> None:
        """Close the file handle."""
        if self.closed:
            return
        self.handler.close()

    @property
    def closed(self) -> bool:
        """Check if the storage is closed."""
        return self.handler.closed


__all__ = ["TomlStorage"]
