from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003

import pytest

from bear_dereth.data_structs.wal import Operation, WALRecord, WriteAheadLog


def _load_wal_records(path: Path) -> list[dict[str, object]]:
    """Return decoded WAL entries from the backing file."""
    raw: str = path.read_text().strip()
    if not raw:
        return []
    return [json.loads(line) for line in raw.splitlines() if line]


def test_write_ahead_log_persists_operations(tmp_path: Path) -> None:
    wal_file: Path = tmp_path / "wal.log"

    with WriteAheadLog(wal_file) as wal:
        first_tx: bool = wal.add_op(0, Operation.INSERT, {"id": 1, "name": "Alice"})
        second_tx: bool = wal.add_op(1, "UPDATE", {"id": 1, "name": "Bob"})
        third_tx: bool = wal.add_op(2, Operation.DELETE, {"id": 2})

    records: list[dict[str, object]] = _load_wal_records(wal_file)
    assert [record["txid"] for record in records] == [0, 1, 2]
    assert [record["op"] for record in records] == ["INSERT", "UPDATE", "DELETE"]
    assert records[0]["data"] == {"id": 1, "name": "Alice"}
    assert records[1]["data"] == {"id": 1, "name": "Bob"}
    assert records[2]["data"] == {"id": 2}
    assert first_tx is True
    assert second_tx is True
    assert third_tx is True


def test_write_ahead_log_start_twice_raises(tmp_path: Path) -> None:
    """Starting an already started WAL raises."""
    wal_file: Path = tmp_path / "wal.log"
    wal: WriteAheadLog[WALRecord] = WriteAheadLog(wal_file)

    try:
        wal.start()
        with pytest.raises(RuntimeError, match="WAL listener already started"):
            wal.start()
    finally:
        wal.stop()
    assert wal._thread is None  # pyright: ignore[reportPrivateUsage]


def test_write_ahead_log_stop_is_idempotent(tmp_path: Path) -> None:
    """Stopping an already stopped WAL is a no-op."""
    wal_file: Path = tmp_path / "wal.log"
    wal: WriteAheadLog[WALRecord] = WriteAheadLog(wal_file)

    wal.stop()
    assert wal._thread is None  # pyright: ignore[reportPrivateUsage]

    wal.start()
    wal.stop()
    wal.stop()
    assert wal._thread is None  # pyright: ignore[reportPrivateUsage]


def test_write_ahead_log_rejects_unknown_operation(tmp_path: Path) -> None:
    wal_file: Path = tmp_path / "wal.log"
    wal: WriteAheadLog[WALRecord] = WriteAheadLog(wal_file)

    with pytest.raises(ValueError, match="NOPE"):
        wal.add_op(1, "NOPE", {"id": 99})
