"""Module providing a JSON Lines formatter for log records."""

from typing import TYPE_CHECKING, Any

from lazy_bear import LazyLoader

if TYPE_CHECKING:
    import json

    from bear_dereth.logger.protocols.formatter import Formatter
    from bear_dereth.logger.records.record import LoggerRecord
else:
    json = LazyLoader("json")
    Formatter = LazyLoader("bear_dereth.logger.protocols.formatter").to("Formatter")
    LoggerRecord = LazyLoader("bear_dereth.logger.records.record").to("LoggerRecord")


class JSONLFormatter(Formatter):
    """A formatter that outputs log records in JSON Lines format."""

    # TODO: Make this configurable to include/exclude certain fields

    def format(self, record: LoggerRecord, **kwargs) -> str:  # type: ignore[override]
        """Format a log record as a JSON Lines string."""
        log_entry: dict[Any, Any] = super().format(record, as_dict=True, **kwargs)
        return json.dumps(log_entry)
