"""Configuration models for Rich Console options."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime  # noqa: TC003
from typing import Any, Literal, TypeGuard

from bear_epoch_time.constants import TIME_FORMAT_WITH_SECONDS
from pydantic import BaseModel, Field
from rich._log_render import FormatTimeCallable
from rich.emoji import EmojiVariant
from rich.style import Style, StyleType
from rich.text import Text
from rich.theme import Theme

from bear_dereth.logger.config._get import LoggerConfig  # noqa: TC001

type HighlighterType = Callable[[str], Text]


class CustomTheme(Theme):
    """A Rich Theme subclass that can be created from a ConfigManager."""

    @classmethod
    def from_config(cls, config: LoggerConfig) -> CustomTheme:
        """Create a CustomTheme from a ConfigManager."""
        return cls(styles=config.theme.model_dump())


ColorSystem = Literal["auto", "standard", "256", "truecolor", "windows"]


class ConsoleOptions(BaseModel):
    """A Pydantic model representing options for a Rich Console."""

    color_system: ColorSystem = "auto"
    force_terminal: bool | None = None
    force_jupyter: bool | None = None
    force_interactive: bool | None = None
    soft_wrap: bool = False
    theme: Theme | CustomTheme | None = CustomTheme()
    no_theme: bool = Field(default=False, exclude=True)
    stderr: bool = False
    quiet: bool = False
    width: int | None = None
    height: int | None = None
    style: StyleType | Style | None = None
    no_color: bool | None = None
    tab_size: int = 8
    record: bool = False
    markup: bool = True
    emoji: bool = True
    emoji_variant: EmojiVariant | None = None
    highlight: bool = True
    log_time: bool = True
    log_path: bool = True
    log_time_format: str | FormatTimeCallable = f"[{TIME_FORMAT_WITH_SECONDS}]"
    highlighter: HighlighterType | None = None
    safe_box: bool = True
    get_datetime: Callable[[], datetime] | None = None
    get_time: Callable[[], float] | None = None

    model_config = {"arbitrary_types_allowed": True}

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        """Override model_dump to exclude None values by default."""
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    def has_theme(self, theme: Theme | CustomTheme | None) -> TypeGuard[Theme | CustomTheme]:
        """Check if a theme is set and use a TypeGuard for type checking."""
        return theme is not None


# ruff: noqa: TC002
