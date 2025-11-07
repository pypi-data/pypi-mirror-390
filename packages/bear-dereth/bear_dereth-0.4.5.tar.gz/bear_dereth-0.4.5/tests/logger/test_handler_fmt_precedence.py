"""Test handler format string precedence."""

from __future__ import annotations

from io import StringIO

from bear_dereth.logger.config import LoggerConfig
from bear_dereth.logger.formatters.template_formatter import TemplateFormatter
from bear_dereth.logger.handlers.console_handler import ConsoleHandler
from bear_dereth.logger.handlers.file_handler import FileHandler


def test_console_handler_fmt_parameter_precedence(tmp_path):
    """Test that fmt parameter takes precedence over config."""
    config = LoggerConfig()

    # Explicit fmt parameter should override config
    custom_fmt = "$level: $msg"
    buffer = StringIO()
    handler = ConsoleHandler(fmt=custom_fmt, file=buffer, config=config)

    assert handler.formatter.fmt == custom_fmt


def test_console_handler_formatter_parameter_precedence(tmp_path):
    """Test that formatter parameter takes highest precedence."""
    config = LoggerConfig()

    # Explicit formatter parameter should take precedence over everything
    custom_fmt = "CUSTOM: $msg"
    custom_formatter = TemplateFormatter(fmt=custom_fmt, config=config)

    buffer = StringIO()
    handler = ConsoleHandler(
        fmt="$level: $msg",  # This should be ignored
        formatter=custom_formatter,
        file=buffer,
        config=config,
    )

    assert handler.formatter.fmt == custom_fmt
    assert handler.formatter is custom_formatter


def test_console_handler_uses_config_default():
    """Test that handler uses config.console.fmt by default."""
    config = LoggerConfig()
    buffer = StringIO()
    handler = ConsoleHandler(file=buffer, config=config)

    # Should use the default from ConsoleHandlerConfig
    assert handler.formatter.fmt == config.console.fmt


def test_file_handler_fmt_parameter_precedence(tmp_path):
    """Test that fmt parameter takes precedence over config."""
    config = LoggerConfig()
    log_file = tmp_path / "test.log"

    # Explicit fmt parameter should override config
    custom_fmt = "$level: $msg"
    handler = FileHandler(file_path=log_file, fmt=custom_fmt, config=config)

    assert handler.formatter.fmt == custom_fmt


def test_file_handler_formatter_parameter_precedence(tmp_path):
    """Test that formatter parameter takes highest precedence."""
    config = LoggerConfig()
    log_file = tmp_path / "test.log"

    # Explicit formatter parameter should take precedence over everything
    custom_fmt = "CUSTOM: $msg"
    custom_formatter = TemplateFormatter(fmt=custom_fmt, config=config)

    handler = FileHandler(
        file_path=log_file,
        fmt="$level: $msg",  # This should be ignored
        formatter=custom_formatter,
        config=config,
    )

    assert handler.formatter.fmt == custom_fmt
    assert handler.formatter is custom_formatter


def test_file_handler_uses_config_default(tmp_path):
    """Test that handler uses config.file.fmt by default."""
    config = LoggerConfig()
    log_file = tmp_path / "test.log"
    handler = FileHandler(file_path=log_file, config=config)

    # Should use the default from FileConfig
    assert handler.formatter.fmt == config.file.fmt
