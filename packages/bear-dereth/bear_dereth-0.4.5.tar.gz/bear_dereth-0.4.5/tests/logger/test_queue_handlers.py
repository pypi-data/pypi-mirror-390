from __future__ import annotations

from queue import Queue
import threading
from types import SimpleNamespace

from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.handlers.queue_handler import QueueHandler
from bear_dereth.logger.handlers.queue_listener import QueueListener
from bear_dereth.logger.records import LoggerRecord, StackInfo
from bear_dereth.sentinels import EXIT_SIGNAL


def make_config(queue: Queue) -> SimpleNamespace:
    return SimpleNamespace(queue=SimpleNamespace(queue=queue))


class DummyHandler:
    def __init__(self) -> None:
        """A minimal handler that records emitted log records."""
        self.name = "dummy"
        self.level = LogLevel.DEBUG
        self.disabled = False
        self.mode = "default"
        self.caller = None
        self.file = None
        self.emitted: list[dict[str, object]] = []

    def emit(self, record: LoggerRecord, **kwargs) -> None:  # noqa: ARG002
        """Capture emitted log records."""
        self.emitted.append(record.model_dump())


def test_queue_listener_processes_records_until_sentinel() -> None:
    queue = Queue()
    handler = DummyHandler()
    errors: list[str] = []

    listener = QueueListener(
        config=make_config(queue),  # type: ignore[arg-type]
        error_callback=lambda message, **kwargs: errors.append(message),
        handlers=[handler],  # type: ignore[arg-type]
        respect_handler_level=False,
    )

    stack: StackInfo = StackInfo.from_current_stack()
    queue.put(LoggerRecord(msg="first", level=LogLevel.INFO, style="", stack_info=stack))
    queue.put(LoggerRecord(msg="second", level=LogLevel.INFO, style="", stack_info=stack))
    queue.put(EXIT_SIGNAL)

    listener._monitor()  # type: ignore[attr-defined]

    assert [rec["msg"] for rec in handler.emitted] == ["first", "second"]
    assert errors == []
    assert queue.empty()


def test_queue_listener_start_and_stop_controls_thread() -> None:
    queue = Queue()
    listener = QueueListener(
        config=make_config(queue),  # type: ignore[arg-type]
        error_callback=lambda *args, **kwargs: None,
    )

    listener.start()
    assert listener._thread is not None  # type: ignore[attr-defined]
    assert listener._thread.is_alive()  # type: ignore[attr-defined]

    listener.stop()
    assert listener._thread is None  # type: ignore[attr-defined]


def test_queue_handler_emit_enqueues_logger_records() -> None:
    queue = Queue()
    errors: list[str] = []

    handler = QueueHandler(
        name="queue",
        error_callback=lambda message, **kwargs: errors.append(message),
        root_level=lambda: LogLevel.INFO,
        handlers=[],
        level=LogLevel.DEBUG,
        queue=queue,
    )

    stack = StackInfo.from_current_stack()
    record = LoggerRecord(msg="hello", style="", level=LogLevel.INFO, stack_info=stack)
    handler.emit(record)

    record = queue.get_nowait()
    assert isinstance(record, LoggerRecord)
    assert record.msg == "hello"
    assert errors == []


def test_queue_handler_respects_level_and_queue_full_errors() -> None:
    queue = Queue(maxsize=1)
    captured: list[tuple[str, dict[str, object]]] = []

    handler = QueueHandler(
        name="queue",
        error_callback=lambda message, **kwargs: captured.append((message, kwargs)),
        root_level=lambda: LogLevel.INFO,
        handlers=[],
        level=LogLevel.INFO,
        queue=queue,
    )

    # Level lower than handler threshold -> should not enqueue
    stack = StackInfo.from_current_stack()
    record_ignored = LoggerRecord(msg="ignored", style="", level=LogLevel.DEBUG, stack_info=stack)
    handler.emit(record_ignored)
    assert queue.empty()

    # Fill queue and trigger put failure
    queue.put(LoggerRecord(msg="existing", style="", level=LogLevel.INFO, stack_info=stack))
    record_fail = LoggerRecord(msg="will-fail", style="", level=LogLevel.INFO, stack_info=stack)
    handler.emit(record_fail)

    assert captured, "Expected an error to be captured"
    assert captured[0][0] == "Error enqueuing log record", "Unexpected error message"


def test_queue_listener_processes_records_from_multiple_threads() -> None:
    queue = Queue()
    handler = DummyHandler()
    errors: list[str] = []

    listener = QueueListener(
        config=make_config(queue),  # type: ignore[arg-type]
        error_callback=lambda message, **kwargs: errors.append(message),
        handlers=[handler],  # type: ignore[arg-type]
    )

    listener.start()

    messages: list[list[str]] = [[f"t1-{i}" for i in range(3)], [f"t2-{i}" for i in range(3)]]

    def producer(batch: list[str]) -> None:
        stack = StackInfo.from_current_stack()
        for msg in batch:
            queue.put(LoggerRecord(msg=msg, level=LogLevel.INFO, style="", stack_info=stack))

    threads = [threading.Thread(target=producer, args=(batch,)) for batch in messages]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    listener.stop()

    emitted_messages: list[object] = [record["msg"] for record in handler.emitted]
    assert sorted(emitted_messages) == sorted(msg for batch in messages for msg in batch)  # type: ignore[arg-type]
    assert errors == []
