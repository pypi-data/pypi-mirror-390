"""A handler for managing multiple tables in the database."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from bear_dereth.datastore.storage import Storage
from bear_dereth.datastore.tables.table import Table

if TYPE_CHECKING:
    from bear_dereth.datastore.unified_data import TableData, UnifiedDataFormat
    from bear_dereth.datastore.wal_config import WALConfig


class TableHandler[T: Storage]:
    """A handler for managing multiple tables in the database."""

    __slots__: tuple = ("data", "enable_wal", "storage", "tables", "wal_config", "wal_dir")

    storage: T
    data: UnifiedDataFormat
    tables: dict[str, Table]
    enable_wal: bool
    wal_dir: str | None
    wal_config: WALConfig | None

    def __init__(
        self,
        storage: T,
        data: UnifiedDataFormat,
        enable_wal: bool = False,
        wal_dir: str | None = None,
        wal_config: Any | None = None,
    ) -> None:
        """Initialize the TableHandler with a storage backend.

        Args:
            storage: An instance of a Storage backend.
            data: The unified data format for all tables
            enable_wal: Enable Write-Ahead Logging for tables
            wal_dir: Directory for WAL files (defaults to storage file directory)
            wal_config: WAL configuration (uses buffered defaults if None)
        """
        self.storage = storage
        self.data = data
        self.tables = {}
        self.enable_wal = enable_wal
        self.wal_dir = wal_dir
        self.wal_config = wal_config

    def write(self) -> None:
        """Write the current state of all tables to storage."""
        self.storage.write(self.data)

    def update_data(self, data: UnifiedDataFormat) -> Self:
        """Update the internal data representation."""
        self.data = data
        return self

    def load(self) -> Self:
        """Load all tables from storage into the handler."""
        for name, table_data in self.data.tables.items():
            table: Table = self.make(name=name, table_data=table_data)
            self.tables[name] = table
        return self

    def new(
        self,
        name: str,
        table_data: TableData,
        enable_wal: bool | None = None,
        wal_file: str | None = None,
    ) -> Table:
        """Create a new empty table and add it to the handler.

        Args:
            name: Name of the new table.
            table_data: The table's data structure
            enable_wal: Enable WAL for this table (overrides handler default if set)
            wal_file: Custom WAL file path (auto-generated if None)

        Returns:
            The newly created Table instance.

        Raises:
            ValueError: If a table with the same name already exists.
        """
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists.")
        table: Table = self.make(name=name, table_data=table_data, enable_wal=enable_wal, wal_file=wal_file)
        self.tables[name] = table
        self.write()
        return table

    def get(self, name: str) -> Table:
        """Get a table by name."""
        if name not in self.tables:
            raise KeyError(f"Table '{name}' does not exist.")
        return self.tables[name]

    def has(self, name: str) -> bool:
        """Check if a table exists."""
        return name in self.tables

    def clear(self) -> None:
        """Clear all tables from the handler."""
        self.data.clear()
        self.tables.clear()

    def make(
        self,
        name: str,
        table_data: TableData,
        enable_wal: bool | None = None,
        wal_file: str | None = None,
    ) -> Table:
        """Map a TableData instance to a Table instance.

        Args:
            name: Table name
            table_data: The table's data structure
            enable_wal: Enable WAL for this table (overrides handler default if set)
            wal_file: Custom WAL file path (auto-generated if None)

        Returns:
            Configured Table instance
        """
        use_wal: bool = enable_wal if enable_wal is not None else self.enable_wal

        wal_path: str | Path | None = None
        if use_wal:
            if wal_file is not None:
                wal_path = wal_file
            else:
                # Auto-generate: use storage file directory or wal_dir if specified
                if self.wal_dir:
                    wal_base = Path(self.wal_dir)
                elif hasattr(self.storage, "file") and self.storage.file:
                    wal_base: Path = Path(self.storage.file).parent
                else:
                    wal_base = Path(".")

                wal_path = wal_base / f"{name}.wal"

        return Table(
            name=name,
            table_data=table_data,
            save_callback=self.write,
            enable_wal=use_wal,
            wal_file_path=wal_path,
            wal_config=self.wal_config,
        )

    def __getattr__(self, name: str) -> Table:
        """Get a table by name."""
        return self.get(name)

    def __setitem__(self, name: str, table: Table) -> None:
        """Set a table by name."""
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists.")
        self.tables[name] = table

    def __delitem__(self, name: str) -> None:
        """Delete a table by name."""
        if name not in self.tables:
            raise KeyError(f"Table '{name}' does not exist.")
        del self.tables[name]

    def __contains__(self, name: str) -> bool:
        """Check if a table exists in the handler."""
        return self.has(name)
