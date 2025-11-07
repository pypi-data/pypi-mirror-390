"""Async queue handler implementation for BearLogger with background processing."""

from __future__ import annotations

from inspect import isclass
from queue import Queue
from typing import TYPE_CHECKING, Any, ClassVar

from bear_dereth.di import Provide, inject
from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.config import Container
from bear_dereth.logger.handlers.queue_listener import QueueListener
from bear_dereth.logger.protocols.handler import Handler

if TYPE_CHECKING:
    from collections.abc import Callable

    from bear_dereth.logger.config import LoggerConfig
    from bear_dereth.logger.records.record import LoggerRecord


class QueueHandler(Handler):
    """A handler that queues messages for async processing by target handlers."""

    default_caller: ClassVar[type[Queue]] = Queue
    caller_attr: ClassVar[str] = "put_nowait"

    @inject
    def __init__(
        self,
        name: str = "queue",
        error_callback: Callable[..., Any] = Provide[Container.error_callback],
        root_level: Callable[[], LogLevel] = Provide[Container.root_level],
        config: LoggerConfig = Provide[Container.config],
        handlers: list[Handler] | None = None,
        level: LogLevel | str | int = LogLevel.DEBUG,
        max_queue_size: int = 1000,
        listener: type[QueueListener] | None = None,
        queue: type[Queue] | Queue | None = None,
        start: bool = False,
    ) -> None:
        """Initialize the QueueHandler with comprehensive DI.

        Args:
            name: Handler name for identification
            error_callback: Callback for handling errors (from DI)
            root_level: Root logging level provider (from DI)
            config: Logger configuration (from DI)
            queue: Queue for async processing (from DI)
            handlers: List of handlers to forward messages to
            level: Minimum logging level for this handler
            max_queue_size: Maximum size of the message queue
        """
        super().__init__()
        self.name: str | None = name
        self.config: LoggerConfig = config
        self.error_callback: Callable[..., Any] = error_callback
        self.get_level: Callable[..., LogLevel] = root_level
        self.level: LogLevel = LogLevel.get(level, default=self.get_level())
        self.max_queue_size: int = max_queue_size
        queue = self.factory() if queue is not None and isclass(queue) else queue
        self.listener: QueueListener = (
            listener(handlers=handlers, queue=queue)
            if listener is not None and isclass(listener)
            else QueueListener(handlers=handlers, queue=queue)
        )
        self.caller = self.file = self.listener.queue  # This is here mostly to shut up the base Handler type checker
        if start:
            self.listener.start()

    @property
    def queue(self) -> Queue:
        """Get the underlying queue used for async processing.

        Returns:
            The Queue instance used by this handler
        """
        return self.listener.queue

    def emit(self, record: LoggerRecord, **kwargs) -> None:  # noqa: ARG002
        """Enqueue a log message for async processing.

        Args:
            record: The LoggerRecord to enqueue
            **kwargs: Additional keyword arguments (ignored in queue handler)
        """
        if self.caller and not self.disabled and self.should_emit(record.level):
            try:
                self.output_func(record)
            except Exception as e:
                self.error_callback("Error enqueuing log record", error=e, name=self.name or "queue_handler")
