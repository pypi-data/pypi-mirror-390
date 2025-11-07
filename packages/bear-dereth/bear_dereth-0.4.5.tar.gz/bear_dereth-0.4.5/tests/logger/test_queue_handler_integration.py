"""Integration tests for QueueHandler and QueueListener."""

from pathlib import Path
import time
from typing import TextIO

from _pytest.capture import CaptureResult
import pytest

from bear_dereth.logger import LogLevel
from bear_dereth.logger.handlers.console_handler import ConsoleHandler
from bear_dereth.logger.handlers.file_handler import FileHandler
from bear_dereth.logger.handlers.queue_handler import QueueHandler
from bear_dereth.logger.handlers.queue_listener import QueueListener
from bear_dereth.logger.rich_printer import BearLogger


class TestQueueHandlerIntegration:
    """Test QueueHandler and QueueListener integration."""

    def test_queue_handler_creation(self, tmp_test_logger: BearLogger):
        """Test that QueueHandler can be created with proper DI."""
        tmp_test_logger.clear_handlers()
        queue_handler = QueueHandler()

        assert queue_handler.name == "queue"
        assert queue_handler.queue is not None
        assert queue_handler.listener is not None  # QueueListener
        assert hasattr(queue_handler.listener, "start")
        assert hasattr(queue_handler.listener, "stop")

    def test_queue_handler_with_target_handlers(self, tmp_test_logger: BearLogger):
        """Test QueueHandler with target handlers."""
        tmp_test_logger.clear_handlers()
        console_handler: ConsoleHandler = ConsoleHandler()
        queue_handler = QueueHandler(handlers=[console_handler])
        listener: QueueListener = queue_handler.listener
        assert len(listener.handlers) == 1
        assert listener.handlers[0] == console_handler
        assert len(queue_handler.listener.handlers) == 1

    def test_queue_handler_logger_integration(self, capsys: pytest.CaptureFixture[str], tmp_test_logger: BearLogger):
        """Test QueueHandler integration with BearLogger."""
        tmp_test_logger.clear_handlers()

        console_handler: ConsoleHandler[TextIO] = ConsoleHandler()
        queue_handler = QueueHandler(handlers=[console_handler])
        tmp_test_logger.add_handler(queue_handler)

        listener: QueueListener = queue_handler.listener
        assert listener is not None
        listener.start()

        try:
            tmp_test_logger.info("test")
            tmp_test_logger.warning("warning")

            time.sleep(0.1)

            captured: CaptureResult[str] = capsys.readouterr()
            assert "test" in captured.out
            assert "warning" in captured.out

        finally:
            queue_handler.listener.stop()

    def test_queue_handler_file_integration(self, tmp_path: Path) -> None:
        """Test QueueHandler with FileHandler target."""
        logger: BearLogger[TextIO] = BearLogger(name="file_test_logger")
        log_file: Path = tmp_path / "queue_test.log"

        logger.clear_handlers()

        file_handler: FileHandler = FileHandler(file_path=log_file)
        queue_handler = QueueHandler(handlers=[file_handler])
        logger.add_handler(queue_handler)

        queue_handler.listener.start()

        try:
            logger.info("Queued file message")
            logger.error("Queued error message")

            time.sleep(0.1)

            assert log_file.exists()
            content: str = log_file.read_text()
            assert "Queued file message" in content
            assert "Queued error message" in content

        finally:
            queue_handler.listener.stop()

    def test_queue_handler_multiple_targets(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        tmp_test_logger: BearLogger,
    ) -> None:
        """Test QueueHandler with multiple target handlers."""
        log_file: Path = tmp_path / "multi_queue_test.log"
        tmp_test_logger.clear_handlers()

        console_handler: ConsoleHandler[TextIO] = ConsoleHandler()
        file_handler: FileHandler = FileHandler(file_path=log_file)
        queue_handler = QueueHandler(handlers=[console_handler, file_handler])
        tmp_test_logger.add_handler(queue_handler)

        queue_handler.listener.start()

        try:
            tmp_test_logger.warning("Multi-target queue message")

            time.sleep(0.1)

            assert log_file.exists()
            file_content: str = log_file.read_text()
            assert "Multi-target queue message" in file_content

            captured: CaptureResult[str] = capsys.readouterr()
            out: str = captured.out.strip().replace("\n", "")
            assert "Multi-target" in out

        finally:
            queue_handler.listener.stop()

    def test_queue_handler_level_filtering(self, capsys: pytest.CaptureFixture[str], tmp_test_logger: BearLogger):
        """Test that QueueHandler respects log levels."""
        tmp_test_logger.clear_handlers()

        console_handler: ConsoleHandler[TextIO] = ConsoleHandler()
        queue_handler = QueueHandler(handlers=[console_handler], level=LogLevel.WARNING)
        tmp_test_logger.add_handler(queue_handler)

        queue_handler.listener.start()

        try:
            tmp_test_logger.debug("Debug message")  # Should be filtered out
            tmp_test_logger.info("Info message")  # Should be filtered out
            tmp_test_logger.warning("Warning message")  # Should pass through
            tmp_test_logger.error("Error message")  # Should pass through

            time.sleep(0.1)

            captured: CaptureResult[str] = capsys.readouterr()
            assert "Debug message" not in captured.out
            assert "Info message" not in captured.out
            assert "Warning message" in captured.out
            assert "Error message" in captured.out

        finally:
            queue_handler.listener.stop()

    def test_queue_listener_context_manager(self, capsys: pytest.CaptureFixture[str]):
        """Test QueueListener as context manager."""
        logger: BearLogger[TextIO] = BearLogger(name="context_test")
        logger.clear_handlers()

        console_handler: ConsoleHandler[TextIO] = ConsoleHandler()
        queue_handler = QueueHandler(handlers=[console_handler])
        logger.add_handler(queue_handler)

        with queue_handler.listener:
            logger.info("Context manager test message")
            time.sleep(0.1)

        captured: CaptureResult[str] = capsys.readouterr()
        out: str = captured.out
        assert out != ""
