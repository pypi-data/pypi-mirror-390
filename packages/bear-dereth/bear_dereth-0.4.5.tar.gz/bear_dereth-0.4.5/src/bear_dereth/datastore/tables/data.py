"""Module defining the TableData class for managing table data in a datastore."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any, Self

from pydantic import Field, computed_field

from bear_dereth.data_structs.counter_class import Counter
from bear_dereth.datastore.columns import Columns, NullColumn
from bear_dereth.datastore.record import Record  # noqa: TC001
from bear_dereth.models.frozen_models import freeze
from bear_dereth.models.general import ExtraIgnoreModel

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class TableData(ExtraIgnoreModel):
    """Complete data for a single table."""

    name: str = Field(default=..., exclude=True)
    columns: list[Columns] = Field(default_factory=list)
    records: list[Record] = Field(default_factory=list)
    primary_col_: Columns = Field(default=NullColumn, exclude=True)
    counter_: Counter | None = Field(default=None, exclude=True, repr=False)

    def _has_one_column(self) -> None:
        """Check if the table has at least one column."""
        if not self.columns:
            raise ValueError(f"Table '{self.name}' must have at least one column.")

    def _validate_table_name(self) -> None:
        """Validate table name format.

        Raises:
            ValueError: If table name is invalid.
        """
        if not self.name or not self.name.strip():
            raise ValueError("Table name cannot be empty or whitespace.")

        if not self.name[0].isalpha() and self.name[0] != "_":
            raise ValueError(f"Table name must start with a letter or underscore, not '{self.name[0]}'.")

        if " " in self.name:
            raise ValueError("Table name cannot contain spaces. Use underscores instead.")

    def _validate_unique_column_names(self) -> None:
        """Validate that all column names are unique.

        Raises:
            ValueError: If duplicate column names are found.
        """
        column_names: list[str] = [col.name for col in self.columns]
        seen: set[str] = set()
        duplicates: set[str] = set()
        for name in column_names:
            if name in seen:
                duplicates.add(name)
            seen.add(name)
        if duplicates:
            raise ValueError(f"Duplicate column names found in table '{self.name}': {sorted(duplicates)}")

    def _validate_exactly_one_primary_key(self) -> None:
        """Validate that exactly one column is designated as primary key.

        Raises:
            ValueError: If zero or multiple primary keys are found.
        """
        primary_keys: list[Columns] = [col for col in self.columns if col.primary_key is True]
        if len(primary_keys) == 0:
            raise ValueError("At least one column must be designated as primary_key=True.")
        if len(primary_keys) > 1:
            pk_names: list[str] = [col.name for col in primary_keys]
            raise ValueError(
                f"Exactly one column must be designated as primary key, found {len(primary_keys)}: {pk_names}"
            )

    def validate_columns(self) -> None:
        """Validate table and column naming and constraints.

        Column/Table Naming Rules:
        - Must start with letter or underscore
        - No spaces (use underscores)
        - Cannot start with 'xml' (case insensitive)
        - Cannot be empty or whitespace-only

        Constraint Rules:
        - Exactly one primary key per table
        - Primary keys cannot be nullable
        - Autoincrement only on integer primary keys

        General:
        - At least one column must be defined
        """
        self._has_one_column()
        self._validate_unique_column_names()
        self._validate_table_name()
        self._validate_exactly_one_primary_key()

    def model_post_init(self, context: Any) -> None:
        """Post-initialization to set up primary column and counter."""
        self.validate_columns()
        if self.primary_col == NullColumn and self.columns:
            self.parse_primary(self.columns)
        if self.counter_ is None and self.is_auto:
            start_value: int = self.highest_primary if self.records else (self.prime_default or 0)
            self.counter_ = Counter(start=start_value)
        return super().model_post_init(context)

    @property
    def counter(self) -> Counter:
        """Get or create the counter for auto-incrementing primary keys."""
        if self.counter_ is None:
            start_value: int = self.highest_primary if self.records else (self.prime_default or 0)
            self.counter_ = Counter(start=start_value)
        return self.counter_

    @computed_field
    def count(self) -> int:
        """Get the count of records in the table."""
        return len(self.records)

    def insert(self, record: Record) -> None:
        """Insert a record into the table."""
        self.records.append(record)

    def delete(self, record: Record) -> None:
        """Delete a record from the table."""
        self.records.remove(record)

    def index(self, record: Record) -> int:
        """Get the index of a record in the table."""
        return self.records.index(record)

    def iterate(self) -> Iterator[Record]:
        """Iterate over the records in the table."""
        return iter(self.records)

    def parse_primary(self, columns: list[Columns]) -> list[Columns]:
        """Parse and set the primary column for the table."""
        primary_key: Columns | None = next((col for col in columns if col.primary_key), None)
        if primary_key is None:
            raise ValueError("At least one column must be designated as primary_key=True.")
        self.set_primary(primary_key)
        if self.is_primary_int and self.prime_default is not None:
            try:
                self.prime_default = int(self.prime_default)
            except Exception:
                self.prime_default = 0
        elif self.primary_col.type == "int" and self.prime_default is None:
            self.prime_default = 0
        return columns

    def set_primary(self, column: Columns) -> None:
        """Set the primary column for the table."""
        self.primary_col_ = column

    @property
    def primary_col(self) -> Columns:
        """Get the primary column object."""
        if self.primary_col_ == NullColumn:
            self.parse_primary(self.columns)
        return self.primary_col_

    @property
    def primary_key(self) -> str:
        """Get the name of the primary key column."""
        return self.primary_col.name

    @property
    def is_auto(self) -> bool:
        """Check if the primary key is auto-incrementing."""
        return self.primary_col.autoincrement is True

    @property
    def is_primary_int(self) -> bool:
        """Check if the primary key column is of type int."""
        return self.primary_col.type == "int"

    @property
    def prime_default(self) -> Any:
        """Get the default value for the primary key column."""
        return self.primary_col.default

    @prime_default.setter
    def prime_default(self, value: Any) -> None:
        """Set the default value for the primary key column."""
        self.primary_col.default = value

    @property
    def highest_primary(self) -> int:
        """Get the highest primary key value in the records, if primary key is int."""
        return max(
            (rec.get(self.primary_key, 0) for rec in self.records if isinstance(rec.get(self.primary_key), int)),
            default=0,
        )

    @classmethod
    def new(cls, name: str, columns: list[Columns]) -> Self:
        """Create a new empty table and add it to the unified data format.

        Args:
            name: Name of the new table.
            columns: Optional list of Columns instances.

        Returns:
            A new TableData instance.
        """
        return cls(name=name, columns=columns)

    def add_record(self, record: Record) -> None:
        """Add a record to a specific table.

        Args:
            record: Dictionary representing the record to add.
        """
        record = self.validate_record(record)
        self.records.append(record)

    def add_records(self, records: list[Record]) -> None:
        """Add multiple records to the table.

        Args:
            records: List of Record instances to add.
        """
        for record in records:
            self.add_record(record)

    def clear(self, choice: str = "records") -> None:
        """Clear the table data.

        Args:
            choice: What to clear. Options are 'records', 'columns', or 'all'.
                     Default is 'records'.
        """
        if choice.lower() in ("records", "all"):
            self.records.clear()
        match choice.lower():
            case "columns":
                self.columns.clear()
                self.primary_col_ = NullColumn
                self.counter_ = None
            case "all":
                self.columns.clear()
                self.primary_col_ = NullColumn
                self.counter_ = None

    def _assign_missing_primary_key(self, setter: Callable) -> None:
        """Assign primary key when missing from record.

        Args:
            setter: Callable to set the primary key value.
        """
        if self.is_auto and self.is_primary_int:
            setter(value=self.counter.tick())
        elif self.prime_default is not None and not self.is_auto:
            setter(value=self.prime_default)
        else:
            raise ValueError(f"Primary key '{self.primary_key}' is required.")

    def _handle_auto_increment(self, setter: Callable, p_key: Any) -> None:
        """Handle auto-increment logic for existing primary key.

        Args:
            setter: Callable to set the primary key value.
            p_key: The current primary key value in the record.
        """
        if p_key < self.highest_primary:
            self.counter.set(self.highest_primary)
        elif p_key and p_key > self.counter.get():
            self.counter.set(int(p_key))
        setter(value=self.counter.tick())

    def _handle_primary_key(self, record: Record) -> None:
        """Handle primary key assignment and auto-increment.

        Args:
            record: The record to validate and potentially modify.

        Returns:
            Self for method chaining.
        """
        setter: Callable = partial(record.set, key=self.primary_key)
        p_key: Any = record.get(self.primary_key)

        if not record.has(self.primary_key):
            self._assign_missing_primary_key(setter)
        elif self.is_auto and self.is_primary_int:
            self._handle_auto_increment(setter, p_key)
        elif self.is_auto and not self.is_primary_int:
            raise ValueError(f"Primary key '{self.primary_key}' must be an integer.")

    def _validate_schema(self, record: Record) -> None:
        """Validate record matches column schema.

        Args:
            record: The record to validate.
        """
        column_names: set[str] = {col.name for col in self.columns}
        required_cols: set[str] = {col.name for col in self.columns if not col.nullable}
        record_keys: set[str] = set(record.keys())

        if unknown := record_keys - column_names:
            raise ValueError(f"Unknown fields: {unknown}. Valid fields: {column_names}")
        if missing := required_cols - record_keys:
            raise ValueError(f"Missing required fields: {missing}")

    def validate_record(self, record: Record) -> Record:
        """Validate record against table schema, adding primary_key if needed."""
        self._handle_primary_key(record)
        self._validate_schema(record)
        return record

    def __len__(self) -> int:
        """Get the number of records in the table."""
        return len(self.records)

    def __hash__(self) -> int:
        """Get the hash of the table based on its name."""
        columns: int = hash(freeze(sorted([hash(column) for column in self.columns])))
        records: int = hash(freeze(sorted([hash(record) for record in self.records])))
        return hash(f"{self.name}-{columns}-{records}")


__all__ = ["TableData"]
