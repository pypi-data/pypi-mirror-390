"""Template-based formatter using string.Template for log messages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lazy_bear import LazyLoader

from bear_dereth.di import Provide, inject
from bear_dereth.logger.protocols import Formatter

if TYPE_CHECKING:
    from bear_dereth.logger.config import LoggerConfig
    from bear_dereth.logger.config.di import Container
    from bear_dereth.logger.config.loggings import FormatterConfig
else:
    Container = LazyLoader("bear_dereth.logger.config.di").to("Container")
    LoggerConfig = LazyLoader("bear_dereth.logger.config._get").to("LoggerConfig")
    FormatterConfig = LazyLoader("bear_dereth.logger.config.loggings").to("FormatterConfig")


class TemplateFormatter(Formatter):
    """A formatter that uses string.Template for flexible log formatting.

    Uses $variable syntax for template substitution, making it easy to create
    readable format strings without worrying about brace escaping.
    """

    @inject
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        exec_fmt: str | None = None,
        config: LoggerConfig = Provide[Container.config],
    ) -> None:
        """Initialize the template formatter.

        Args:
            name: Optional name for the formatter
            fmt: Format template string (falls back to config.console_fmt)
            exec_fmt: Exception template string (falls back to config.exec_fmt)
            config: Formatter configuration (uses defaults if not provided)
        """
        fmt_config: FormatterConfig = config.formatter
        super().__init__(
            fmt=fmt or fmt_config.console_fmt,
            datefmt=datefmt or fmt_config.datefmt,
            exec_fmt=exec_fmt or fmt_config.exception_fmt,
            config=fmt_config,
        )

    def __repr__(self) -> str:
        """String representation of the formatter."""
        return f"TemplateFormatter(name={self.name!r}, fmt={self.fmt!r})"
