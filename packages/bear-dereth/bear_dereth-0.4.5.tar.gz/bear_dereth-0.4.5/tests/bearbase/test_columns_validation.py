"""Test to reproduce column duplication issue."""

from pathlib import Path

import pytest

from bear_dereth.datastore.record import Record
from bear_dereth.datastore.storage.toml import TomlStorage
from bear_dereth.datastore.storage.xml import XMLStorage
from bear_dereth.datastore.unified_data import HeaderData, TableData, UnifiedDataFormat


def test_simple_write_read_columns(tmp_path: Path) -> None:
    """Test that a simple write and read preserves column count."""
    data = UnifiedDataFormat(
        header=HeaderData(version="0.1.0", tables=["settings"]),
        tables={
            "settings": TableData(
                name="settings",
                columns=[
                    {"name": "id", "type": "int", "nullable": False, "primary_key": True},
                    {"name": "key", "type": "str", "nullable": False},
                    {"name": "value", "type": "str", "nullable": False},
                    {"name": "type", "type": "str", "nullable": False},
                ],  # pyright: ignore[reportArgumentType]
                records=[
                    {"id": 1, "key": "test", "value": "hello", "type": "str"},
                ],  # pyright: ignore[reportArgumentType]
            )
        },
    )

    assert len(data.tables["settings"].columns) == 4
    toml_path: Path = tmp_path / "test_duplication.toml"
    toml_storage = TomlStorage(toml_path, file_mode="w+", encoding="utf-8")
    toml_storage.write(data)

    toml_storage.close()
    xml_path: Path = tmp_path / "test_duplication.xml"
    xml_storage = XMLStorage(xml_path, file_mode="w+", encoding="utf-8")
    xml_storage.write(data)

    xml_storage.close()
    assert len(data.tables["settings"].columns) == 4, f"Expected 4 columns, got {len(data.tables['settings'].columns)}"
    toml_storage = TomlStorage(toml_path, file_mode="r", encoding="utf-8")
    loaded_toml: UnifiedDataFormat | None = toml_storage.read()
    toml_storage.close()

    xml_storage = XMLStorage(xml_path, file_mode="r", encoding="utf-8")
    loaded_xml: UnifiedDataFormat | None = xml_storage.read()
    xml_storage.close()

    assert loaded_toml is not None
    assert len(loaded_toml.tables["settings"].columns) == 4
    assert loaded_xml is not None
    assert len(loaded_xml.tables["settings"].columns) == 4


def test_duplicate_column_names_rejected() -> None:
    """Test that TableData rejects duplicate column names."""
    with pytest.raises(ValueError, match="Duplicate column names found"):
        TableData(
            name="test_table",
            columns=[
                {"name": "id", "type": "int", "nullable": False, "primary_key": True},
                {"name": "name", "type": "str", "nullable": False},
                {"name": "name", "type": "str", "nullable": False},  # duplicate!
            ],  # pyright: ignore[reportArgumentType]
        )


def test_multiple_duplicate_column_names_rejected() -> None:
    """Test that TableData reports all duplicate column names."""
    with pytest.raises(ValueError, match="'id', 'name'"):
        TableData(
            name="test_table",
            columns=[
                {"name": "id", "type": "int", "nullable": False, "primary_key": True},
                {"name": "name", "type": "str", "nullable": False},
                {"name": "id", "type": "int", "nullable": False},
                {"name": "name", "type": "str", "nullable": False},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_no_primary_key_rejected() -> None:
    """Test that TableData requires at least one primary key."""
    with pytest.raises(ValueError, match="At least one column must be designated as primary_key=True"):
        TableData(
            name="test_table",
            columns=[
                {"name": "id", "type": "int", "nullable": False},
                {"name": "name", "type": "str", "nullable": False},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_multiple_primary_keys_rejected() -> None:
    """Test that TableData rejects multiple primary keys."""
    with pytest.raises(ValueError, match="Exactly one column must be designated as primary key"):
        TableData(
            name="test_table",
            columns=[
                {"name": "id", "type": "int", "nullable": False, "primary_key": True},
                {"name": "uuid", "type": "str", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_nullable_primary_key_rejected() -> None:
    """Test that primary key cannot be nullable."""
    with pytest.raises(ValueError, match="Primary key column 'id' cannot be nullable"):
        TableData(
            name="test_table",
            columns=[
                {"name": "id", "type": "int", "nullable": True, "primary_key": True},
                {"name": "name", "type": "str", "nullable": False},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_autoincrement_on_non_primary_key_rejected() -> None:
    """Test that autoincrement requires primary_key=True."""
    with pytest.raises(ValueError, match="Autoincrement can only be set on primary key columns"):
        TableData(
            name="test_table",
            columns=[
                {"name": "id", "type": "int", "nullable": False, "primary_key": True},
                {"name": "counter", "type": "int", "nullable": False, "autoincrement": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_autoincrement_on_non_integer_rejected() -> None:
    """Test that autoincrement requires integer type."""
    with pytest.raises(ValueError, match="Autoincrement can only be set on integer columns"):
        TableData(
            name="test_table",
            columns=[
                {"name": "id", "type": "str", "nullable": False, "primary_key": True, "autoincrement": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_empty_column_name_rejected() -> None:
    """Test that column names cannot be empty."""
    with pytest.raises(ValueError, match="Column name cannot be empty"):
        TableData(
            name="test_table",
            columns=[
                {"name": "", "type": "int", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_whitespace_only_column_name_rejected() -> None:
    """Test that column names cannot be only whitespace."""
    with pytest.raises(ValueError, match="Column name cannot be empty"):
        TableData(
            name="test_table",
            columns=[
                {"name": "   ", "type": "int", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_column_name_starting_with_number_rejected() -> None:
    """Test that column names cannot start with a number."""
    with pytest.raises(ValueError, match="Column name must start with a letter or underscore"):
        TableData(
            name="test_table",
            columns=[
                {"name": "123_id", "type": "int", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_column_name_with_spaces_rejected() -> None:
    """Test that column names cannot contain spaces."""
    with pytest.raises(ValueError, match="Column name cannot contain spaces"):
        TableData(
            name="test_table",
            columns=[
                {"name": "my field", "type": "int", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_column_name_starting_with_xml_rejected() -> None:
    """Test that column names cannot start with 'xml'."""
    with pytest.raises(ValueError, match="Column name cannot start with 'xml'"):
        TableData(
            name="test_table",
            columns=[
                {"name": "xmlData", "type": "int", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_empty_table_name_rejected() -> None:
    """Test that table names cannot be empty."""
    with pytest.raises(ValueError, match="Table name cannot be empty"):
        TableData(
            name="",
            columns=[
                {"name": "id", "type": "int", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_table_name_with_spaces_rejected() -> None:
    """Test that table names cannot contain spaces."""
    with pytest.raises(ValueError, match="Table name cannot contain spaces"):
        TableData(
            name="my table",
            columns=[
                {"name": "id", "type": "int", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_table_name_starting_with_number_rejected() -> None:
    """Test that table names cannot start with a number."""
    with pytest.raises(ValueError, match="Table name must start with a letter or underscore"):
        TableData(
            name="123_table",
            columns=[
                {"name": "id", "type": "int", "nullable": False, "primary_key": True},
            ],  # pyright: ignore[reportArgumentType]
        )


def test_table_with_no_columns_rejected() -> None:
    """Test that tables must have at least one column."""
    with pytest.raises(ValueError, match="Table 'empty_table' must have at least one column"):
        TableData(name="empty_table")


def test_record_missing_non_nullable_field_rejected():
    """Test that records must provide values for non-nullable columns."""
    table = TableData(
        name="users",
        columns=[
            {"name": "id", "type": "int", "nullable": False, "primary_key": True},
            {"name": "username", "type": "str", "nullable": False},
            {"name": "email", "type": "str", "nullable": True},
        ],  # pyright: ignore[reportArgumentType]
    )

    with pytest.raises(ValueError, match="Missing required fields: \\{'username'\\}"):
        table.add_record(Record(id=1, email="test@example.com"))


def test_record_with_nullable_field_omitted_accepted():
    """Test that records can omit nullable columns."""
    table = TableData(
        name="users",
        columns=[
            {"name": "id", "type": "int", "nullable": False, "primary_key": True},
            {"name": "username", "type": "str", "nullable": False},
            {"name": "email", "type": "str", "nullable": True},
        ],  # pyright: ignore[reportArgumentType]
    )

    table.add_record(Record(id=1, username="john_doe"))
    assert len(table.records) == 1
    assert table.records[0]["username"] == "john_doe"
