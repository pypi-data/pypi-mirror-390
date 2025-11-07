"""A set of logging handlers for different output targets."""

from .buffer_handler import BufferHandler
from .console_handler import ConsoleHandler
from .file_handler import FileHandler
from .queue_handler import QueueHandler

# TODO: MAKE HANDLERS MORE CONSISTENT WITH EACH OTHER REGARDING CALLER HANDLING

__all__ = ["BufferHandler", "ConsoleHandler", "FileHandler", "QueueHandler"]
