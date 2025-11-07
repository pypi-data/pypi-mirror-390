"""A WAL( Write-Ahead Log) data structure implementation."""

from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
import queue
from queue import Queue
from threading import Event, Thread
import time
from typing import TYPE_CHECKING, Any, Self
import zlib

from bear_epoch_time import EpochTimestamp
from funcy_bear.files.jsonl.file_handler import JSONLFilehandler
from funcy_bear.files.text.file_handler import TextFileHandler
from lazy_bear import LazyLoader
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer, field_validator

from bear_dereth.data_structs.autosort_list import AutoSort
from bear_dereth.datastore.wal_config import WALConfig, WALFlushMode
from bear_dereth.sentinels import EXIT_SIGNAL

if TYPE_CHECKING:
    from contextlib import suppress
    import json
else:
    json = LazyLoader("json")
    suppress = LazyLoader("contextlib").to("suppress")


def compute_checksum(data: str) -> str:
    """Compute a checksum for the given data string."""
    return str(zlib.crc32(data.encode("utf-8")) & 0xFFFFFFFF)


class Operation(StrEnum):
    """Enumeration of WAL operations."""

    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    COMMIT = "COMMIT"


class WALRecord(BaseModel):
    """A record in the Write-Ahead Log."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    txid: int
    op: Operation
    data: dict[str, Any] | None = Field(default=None)
    timestamp: EpochTimestamp = Field(default_factory=EpochTimestamp.now)

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, value: Any) -> EpochTimestamp:
        """Validate and convert the timestamp field to EpochTimestamp."""
        if isinstance(value, int):
            return EpochTimestamp(value)
        if isinstance(value, EpochTimestamp):
            return value
        raise TypeError("timestamp must be an int or EpochTimestamp")

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: EpochTimestamp) -> int:
        """Serialize the timestamp field to an integer."""
        return int(value)

    @computed_field
    def checksum(self) -> str:
        """Compute a checksum for the WALRecord."""
        record_json: str = self.model_dump_json(exclude={"checksum"}, exclude_none=True)
        return compute_checksum(record_json)

    def __str__(self) -> str:
        """String representation of the WALRecord."""
        output: str = f"WALRecord(txid={self.txid}, op={self.op}"
        if self.data is not None:
            output += f", data={self.data}"
        output += f", timestamp={int(self.timestamp)})"
        return output

    def __repr__(self) -> str:
        """Official string representation of the WALRecord."""
        return self.__str__()


class WriteAheadLog[T = WALRecord]:
    """A simple Write-Ahead Log (WAL) implementation with configurable flush strategies."""

    def __init__(
        self,
        file: str | Path,
        record_t: Callable[..., T] = WALRecord,
        config: WALConfig | None = None,
    ) -> None:
        """Initialize the Write-Ahead Log.

        Args:
            file: Path to WAL file
            record_t: Record class factory
            config: WAL configuration (uses buffered defaults if None)
        """
        self._log_queue: Queue = Queue()
        self._writer: TextFileHandler = TextFileHandler(file, touch=True)
        self._reader: JSONLFilehandler[dict] = JSONLFilehandler(file)
        self._thread: Thread | None = None
        self._flush_thread: Thread | None = None
        self._running: bool = False
        self._stop_event: Event = Event()
        self.default_class: Callable[..., T] = record_t
        self.config: WALConfig = config or WALConfig.buffered()
        self._op_count: int = 0
        self._buffer: list[str] = []

    def commit(self, txid: int) -> bool:
        """Log a COMMIT operation to the WAL.

        Args:
            txid: The transaction ID to commit

        Returns:
            True if the commit operation was successfully logged
        """
        try:
            self._log_queue.put(WALRecord(txid=txid, op=Operation.COMMIT))
            return True
        except Exception:
            return False

    def add_op(self, txid: int, op: Operation | str, data: dict[str, Any]) -> bool:
        """Log an operation to the WAL.

        Args:
            txid: The transaction ID
            op: The operation to log (Operation enum or string)
            data: The data associated with the operation

        Returns:
            True if the operation was successfully logged
        """
        try:
            if isinstance(op, str):
                op = Operation(op)
            record: WALRecord = WALRecord(txid=txid, op=op, data=data)
            self._log_queue.put(record)
            return True
        except ValueError as e:
            raise ValueError(f"Invalid operation '{op}': {e}") from e

    def _write(self, record: WALRecord) -> None:
        """Write a single WAL record to the file.

        Behavior depends on flush_mode:
        - IMMEDIATE: fsync after every write (slow, maximum safety)
        - BUFFERED: batch in memory, flush periodically (fast, small crash window)

        Args:
            record: The WALRecord to write
        """
        try:
            serialized: str = record.model_dump_json(exclude_none=True)
            if self.config.flush_mode == WALFlushMode.IMMEDIATE:
                self._writer.append(serialized, force=True)  # flush to disk immediately
            elif self.config.flush_mode == WALFlushMode.BUFFERED:
                # TODO(bear): Consider adding memory limit in addition to batch size.
                # In high-throughput scenarios with large records, the buffer could
                # consume significant memory before hitting batch_size threshold.
                # Could track buffer size in bytes and flush when exceeding limit.
                self._buffer.append(serialized)
                self._op_count += 1

                if self._op_count >= self.config.flush_batch_size:  # Flush if batch size reached
                    self._flush_buffer()

        except Exception as e:
            raise OSError(f"Failed to write WAL record {record}: {e}") from e

    def _flush_buffer(self) -> None:
        """Flush buffered WAL records to disk."""
        if not self._buffer:
            return
        try:
            for line in self._buffer:
                self._writer.append(line, force=False)
            self._writer.flush()  # Single fsync for entire batch
            self._buffer.clear()
            self._op_count = 0
        except Exception as e:
            raise OSError(f"Failed to flush WAL buffer: {e}") from e

    def read_all(self, sort_key: Callable[[dict], Any] | None = None) -> AutoSort[dict]:
        """Read all WAL records from the file.

        Basically this would be used during recovery to replay the log.

        Args:
            sort_key: Optional callable to sort records (default: by timestamp, txid)

        Returns:
            A list of WALRecord objects read from the file
        """

        def _default_key(r: dict) -> tuple[int, ...]:
            """Default sort key: (timestamp, txid)."""
            return r.get("timestamp", 0), r.get("txid", 0)

        records: AutoSort[dict] = AutoSort(key=sort_key or _default_key)
        try:
            records.extend(self._reader.readlines())
            return records
        except Exception as e:
            raise OSError(f"Failed to read WAL records: {e}") from e

    def _loop(self) -> None:
        """Write log records to the file."""
        q: Queue = self._log_queue
        has_task_done: bool = hasattr(q, "task_done")
        while True:
            try:
                record: WALRecord = q.get()
                if record is EXIT_SIGNAL:
                    self._flush_buffer()
                    if has_task_done:
                        q.task_done()
                    break
                self._write(record)
                if has_task_done:
                    q.task_done()
            except queue.Empty:
                continue

    def _flush_loop(self) -> None:
        """Periodically flush WAL buffer in BUFFERED mode."""
        if self.config.flush_mode != WALFlushMode.BUFFERED:
            return

        while not self._stop_event.is_set():  # Wait for flush_interval or stop signal
            if self._stop_event.wait(timeout=self.config.flush_interval):
                break  # Stop event set, exit

            if self._buffer:
                # TODO(bear): Improve error handling - log errors, implement retry logic,
                # or expose flush failures through a callback/event system
                with suppress(Exception):
                    self._flush_buffer()

    def start(self) -> None:
        """Start the WAL logging threads."""
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("WAL listener already started")

        self._stop_event.clear()
        self._running = True

        self._thread = t = Thread(target=self._loop)
        t.daemon = True
        t.start()

        if self.config.flush_mode == WALFlushMode.BUFFERED:
            self._flush_thread = ft = Thread(target=self._flush_loop)
            ft.daemon = True
            ft.start()

    def stop(self) -> None:
        """Stop the WAL threads and flush remaining buffer."""
        self._stop_event.set()
        self._running = False

        if self._flush_thread is not None:
            self._flush_thread.join(timeout=1.0)
            self._flush_thread = None

        if self._thread is not None:
            self.enqueue_sentinel()
            self._thread.join()
            self._thread = None

    def clear(self) -> None:
        """Clear the WAL file.

        This should happen after it is confirmed that all operations are committed.
        """
        self._writer.clear()

    def enqueue_sentinel(self) -> None:
        """Enqueue a sentinel object to stop thread."""
        self._log_queue.put(EXIT_SIGNAL)

    def wait_for_idle(self, timeout: float = 5.0, flush_buffer: bool = True) -> bool:
        """Wait for all queued operations to be processed.

        Useful for testing to ensure WAL operations are flushed to disk
        before checking file contents.

        Args:
            timeout: Maximum time to wait in seconds (default: 5.0)
            flush_buffer: If True, also flush buffer in BUFFERED mode (default: True)

        Returns:
            True if queue became empty within timeout, False otherwise
        """
        start_time: float = time.time()
        while not self._log_queue.empty():
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.001)  # avoid busy waiting

        if flush_buffer and self.config.flush_mode == WALFlushMode.BUFFERED:
            self._flush_buffer()  # In BUFFERED mode, also flush any pending buffer

        time.sleep(0.01)  # tiny bit more time for final disk sync
        return True

    def __enter__(self) -> Self:
        """Enter the context manager."""
        self.start()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit the context manager."""
        self.stop()
