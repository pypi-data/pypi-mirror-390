from contextlib import redirect_stdout
from io import StringIO
from typing import Any, TextIO

import pytest
from rich.style import Style
from rich.theme import Theme

from bear_dereth.logger.config import ConsoleOptions, CustomTheme, LoggerConfig
from bear_dereth.logger.rich_printer import BearLogger


@pytest.mark.visual
def test_logger_logging_visual(tmp_logger: BearLogger[Any]):
    logger: BearLogger[Any] = tmp_logger

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.success("This is a success message")
    logger.failure("This is a failure message")


class TestConfig:
    def test_custom_theme_creation(self, tmp_logger_config: LoggerConfig) -> None:
        """Test CustomTheme creation from config."""
        theme: CustomTheme = CustomTheme.from_config(tmp_logger_config)
        assert isinstance(theme, Theme), "CustomTheme should create a Rich Theme instance"
        theme_styles: dict[str, Style] = theme.styles
        expected_styles: list[str] = ["info", "warning", "error", "debug", "success", "failure", "exception"]
        for style in expected_styles:
            assert style in theme_styles, f"Rich theme should contain style '{style}'"

    def test_default_config_loads(self, tmp_logger_config: LoggerConfig) -> None:
        """Test that default config loads with expected theme styles."""
        theme_dict: dict[str, Any] = tmp_logger_config.theme.model_dump()
        expected_styles: list[str] = ["info", "warning", "error", "debug", "success", "failure", "exception"]
        for style in expected_styles:
            assert style in theme_dict, f"Style '{style}' should be in theme config"
            assert theme_dict[style], f"Style '{style}' should have a non-empty value"


def test_logger_initialization(tmp_logger: BearLogger[Any]) -> None:
    logger: BearLogger[Any] = tmp_logger
    assert logger.name is None
    assert logger.level.name == "DEBUG"
    assert isinstance(logger.handlers, list)
    assert len(logger.handlers) > 0  # Default console handler should be present
    assert hasattr(logger, "info")
    assert isinstance(logger.config, LoggerConfig)
    assert isinstance(logger.theme, CustomTheme)
    assert isinstance(logger.console_options, ConsoleOptions)


def test_logger_methods(tmp_logger: BearLogger[Any]):
    logger: BearLogger[Any] = tmp_logger

    for method in ["debug", "info", "warning", "error", "success", "failure", "exception"]:
        assert hasattr(logger, method)
        assert callable(getattr(logger, method))


def test_logger_logging(tmp_logger: BearLogger[Any]) -> None:
    logger: BearLogger[TextIO] = tmp_logger

    capture = StringIO()

    with redirect_stdout(capture):
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")
        logger.success("success")
        logger.failure("failure")

    captured: str = capture.getvalue().strip().replace("\n", " ")
    assert "debug" in captured
    assert "info" in captured
    assert "warning" in captured
    assert "error" in captured
    assert "success" in captured
    assert "failure" in captured
