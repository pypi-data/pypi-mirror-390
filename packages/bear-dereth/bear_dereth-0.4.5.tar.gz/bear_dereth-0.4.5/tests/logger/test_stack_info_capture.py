"""Test stack_info capture and propagation through handlers."""

from __future__ import annotations

from queue import Queue
import time
from typing import TYPE_CHECKING, Any

from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.handlers.file_handler import FileHandler
from bear_dereth.logger.handlers.queue_handler import QueueHandler
from bear_dereth.logger.records import LoggerRecord
from bear_dereth.logger.records.stack_info import StackInfo
from bear_dereth.logger.rich_printer import BearLogger

if TYPE_CHECKING:
    from pathlib import Path


class StackInfoCapturingHandler:
    """A test handler that captures stack_info from emit calls."""

    def __init__(self) -> None:
        """Initialize the capturing handler."""
        self.name = "stack_info_capturer"
        self.level = LogLevel.DEBUG
        self.disabled = False
        self.mode = "default"
        self.caller = None
        self.file = None
        self.captured_stack_infos: list[Any | None] = []
        self.captured_messages: list[str] = []

    def emit(self, record: LoggerRecord, **kwargs) -> None:  # noqa: ARG002
        """Capture the stack_info from the record."""
        self.captured_stack_infos.append(record.stack_info)
        self.captured_messages.append(str(record.msg))


def test_stack_info_captured_in_direct_handler():
    """Test that stack_info is captured when logging directly to a handler."""
    logger = BearLogger(name="direct_test")
    logger.clear_handlers()

    capturer = StackInfoCapturingHandler()
    logger.add_handler(capturer)  # type: ignore[arg-type]

    logger.info("Test message")

    assert len(capturer.captured_stack_infos) == 1
    stack_info: StackInfo | None = capturer.captured_stack_infos[0]
    assert stack_info is not None
    assert isinstance(stack_info, StackInfo)
    assert stack_info.caller_function == "test_stack_info_captured_in_direct_handler"
    assert "test_stack_info_capture.py" in stack_info.filename


def test_stack_info_captured_in_queue_handler():
    """Test that stack_info is captured and passed through queue handler."""
    queue: Queue = Queue()

    logger = BearLogger(name="queue_test")
    logger.clear_handlers()
    capturer = StackInfoCapturingHandler()
    queue_handler = QueueHandler(
        handlers=[capturer],  # type: ignore[arg-type]
        start=True,
        queue=queue,
    )

    logger.add_handler(queue_handler)

    logger.info("Queue test message")

    # Give queue time to process

    time.sleep(0.1)

    queue_handler.listener.stop()

    assert len(capturer.captured_stack_infos) == 1
    stack_info: StackInfo | None = capturer.captured_stack_infos[0]
    assert stack_info is not None
    assert isinstance(stack_info, StackInfo)
    assert stack_info.caller_function == "test_stack_info_captured_in_queue_handler"
    assert "test_stack_info_capture.py" in stack_info.filename


def test_queue_handler_emit_with_stack_info() -> None:
    """Test that QueueHandler.emit properly handles stack_info in kwargs."""
    queue: Queue = Queue()
    errors: list[str] = []

    handler = QueueHandler(
        name="queue",
        error_callback=lambda message, **kwargs: errors.append(message),
        root_level=lambda: LogLevel.INFO,
        handlers=[],
        level=LogLevel.DEBUG,
        queue=queue,
    )

    # Emit with auto-created stack_info
    stack = StackInfo.from_current_stack()
    record = LoggerRecord(msg="hello", style="", level=LogLevel.INFO, stack_info=stack)
    handler.emit(record)

    assert queue.qsize() == 1, f"Expected 1 item in queue, got {queue.qsize()}. Errors: {errors}"

    record = queue.get_nowait()
    assert record.msg == "hello"
    assert record.stack_info is not None
    assert errors == []


def test_queue_handler_emit_with_existing_stack_info():
    """Test that QueueHandler doesn't duplicate stack_info if already present."""
    queue = Queue()
    errors: list[str] = []

    handler = QueueHandler(
        name="queue",
        error_callback=lambda message, **kwargs: errors.append(message),
        root_level=lambda: LogLevel.INFO,
        queue=queue,
        handlers=[],
        level=LogLevel.DEBUG,
    )

    # Create a stack_info manually
    stack_info = StackInfo.from_current_stack()

    # Emit with existing stack_info in record
    record = LoggerRecord(msg="hello", style="", level=LogLevel.INFO, stack_info=stack_info)
    handler.emit(record)

    assert queue.qsize() == 1, f"Expected 1 item in queue, got {queue.qsize()}. Errors: {errors}"

    dequeued_record = queue.get_nowait()
    assert dequeued_record.msg == "hello"
    assert dequeued_record.stack_info.caller_function == stack_info.caller_function  # Should have same data
    assert errors == []


def test_console_handler_pops_stack_info():
    """Test that ConsoleHandler properly handles stack_info from record."""
    logger = BearLogger(name="console_test", level="DEBUG")
    logger.info("test")


def test_file_handler_pops_stack_info(tmp_path: Path) -> None:
    """Test that FileHandler properly handles stack_info from record."""
    BearLogger(name="console_test")
    log_file: Path = tmp_path / "test.log"
    handler = FileHandler(file_path=log_file)
    stack_info: StackInfo = StackInfo.from_current_stack()

    # This should not raise an error
    record = LoggerRecord(msg="test", style="info", level=LogLevel.INFO, stack_info=stack_info)
    handler.emit(record)

    handler.close()


def test_debug_queue_handler_emit_issue() -> None:
    """Debug test to verify queue handler emit works correctly."""
    queue = Queue()
    errors: list[tuple[str, dict]] = []

    def capture_error(message: str, **kwargs) -> None:
        errors.append((message, kwargs))

    handler = QueueHandler(
        name="queue",
        error_callback=capture_error,
        root_level=lambda: LogLevel.INFO,
        handlers=[],
        level=LogLevel.DEBUG,
        queue=queue,
    )
    stack: StackInfo = StackInfo.from_current_stack()
    record = LoggerRecord(msg="hello", style="", level=LogLevel.INFO, stack_info=stack)
    handler.emit(record)
    assert queue.qsize() == 1, f"Queue should have 1 item but has {queue.qsize()}. Errors: {errors}"
