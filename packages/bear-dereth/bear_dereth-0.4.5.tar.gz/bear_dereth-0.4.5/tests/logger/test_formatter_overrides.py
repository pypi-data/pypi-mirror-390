"""Tests for per-handler and global formatter overrides."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from bear_epoch_time import EpochTimestamp
from bear_epoch_time.tz import TimeZoneHelper

from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.config import LoggerConfig
from bear_dereth.logger.config.di import get_config_manager, get_default_config
from bear_dereth.logger.handlers.console_handler import ConsoleHandler
from bear_dereth.logger.handlers.file_handler import FileHandler
from bear_dereth.logger.records import LoggerRecord, StackInfo
from bear_dereth.logger.records.time_helper import TimeHelper

if TYPE_CHECKING:
    from pathlib import Path


def test_console_handler_fmt_override() -> None:
    buf = StringIO()
    fmt = "$level $filename:$line_number $msg"

    config_manager = get_config_manager(program_name="logger", env="test")
    cfg: LoggerConfig = get_default_config(config_manager)
    handler: ConsoleHandler[StringIO] = ConsoleHandler(file=buf, fmt=fmt, config=cfg)

    stack: StackInfo = StackInfo.from_current_stack()
    record = LoggerRecord(msg="hello", style="info", level=LogLevel.INFO, stack_info=stack)
    handler.emit(record)

    out = buf.getvalue()
    assert "INFO" in out
    assert "test_formatter_overrides.py" in out
    assert "hello" in out


def test_file_handler_fmt_override(tmp_path: Path) -> None:
    log_file: Path = tmp_path / "fmt.log"
    fmt = "$level $filename:$line_number $msg"
    handler: FileHandler = FileHandler(file_path=log_file, fmt=fmt)

    stack: StackInfo = StackInfo.from_current_stack()
    record = LoggerRecord(msg="world", style="info", level=LogLevel.INFO, stack_info=stack)
    handler.emit(record)

    handler.close()
    text: str = log_file.read_text()
    # Remove whitespace/line breaks for easier matching
    text_normalized: str = "".join(text.split())
    assert "INFO" in text
    assert "test_formatter_overrides.py" in text_normalized or "formatter_overrides.py" in text
    assert "world" in text


def test_verbose_fmt(tmp_path: Path) -> None:
    log_file: Path = tmp_path / "verbose.log"
    fmt = "$timestamp $time $date $tz $msg $style $level $caller_function $line_number $filename $fullpath $relative_path $python_path $code_line $location $full_location $path $code_context $index $stack_value $exec_frame"
    handler = FileHandler(file_path=log_file, fmt=fmt)
    set_time: EpochTimestamp = EpochTimestamp.from_iso_string("2025-10-22T20:37:44+00:00")
    stack: StackInfo = StackInfo.from_current_stack()
    record = LoggerRecord(msg="verbose test", style="debug", level=LogLevel.DEBUG, stack_info=stack, timestamp=set_time)
    handler.emit(record)
    handler.close()

    # We have to do this because we default to the local user's timezone in the formatter
    tz = TimeZoneHelper()
    local_tz = tz.local_tz
    check: Literal["08:37:44 PM", "01:37:44 PM"] = "08:37:44 PM" if str(local_tz) == "UTC" else "01:37:44 PM"

    helper = TimeHelper()

    text: str = log_file.read_text()
    assert f"10-22-2025 {check} " in text
    assert f"{check} " in text
    assert "10-22-2025 " in text
    assert str(helper.tz) in text
    assert "verbose test " in text
    assert "debug " in text
    assert "DEBUG " in text
    assert "test_verbose_fmt " in text
    assert "test_formatter_overrides.py " in text
    assert "tests/logger/test_formatter_overrides.py " in text
    assert "tests.logger.test_formatter_overrides " in text
    assert "stack: StackInfo = StackInfo.from_current_stack() " in text
    assert "test_formatter_overrides.py" in text
    assert "@test_verbose_fmt " in text
    assert "stack: StackInfo = StackInfo.from_current_stack()\\n'] " in text
    assert "0 " in text
    assert "1 " in text
    assert "Frame(test_verbose_fmt at " in text

    record_dict = record.model_dump_json()

    back_into_model = LoggerRecord.model_validate_json(record_dict)
