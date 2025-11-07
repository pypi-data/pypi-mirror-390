"""A Pydantic model representing color themes for the logger."""

from bear_dereth.models import FrozenModel


class CyberTheme(FrozenModel):
    """Namespace for cyberpunk color theme constants."""

    primary: str = "bright_magenta"
    neon_green: str = "bright_green"
    neon_cyan: str = "bright_cyan"
    warning: str = "bright_yellow"
    error: str = "bright_red"
    credits: str = "bright_yellow"
    data: str = "bright_blue"
    system: str = "dim white"


class LoggerTheme(FrozenModel):
    """A Pydantic model representing a theme for logging."""

    info: str = "bold blue"
    warning: str = "bold yellow"
    error: str = "bold red"
    debug: str = "bold magenta"
    success: str = "bold green"
    failure: str = "bold red"
    exception: str = "underline bold red"
    verbose: str = "dim white"


__all__ = ["CyberTheme", "LoggerTheme"]
