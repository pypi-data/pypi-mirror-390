"""Basic logger using the Rich library."""

from rich import inspect
from rich.console import Console
from rich.theme import Theme

from bear_dereth.dynamic_meth import dynamic_methods
from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.protocols import TypeLogger

THEME: dict[str, dict[str, str | LogLevel]] = {
    "info": {"level": LogLevel.INFO, "style": "bold green"},
    "debug": {"level": LogLevel.DEBUG, "style": "bold blue"},
    "warning": {"level": LogLevel.WARNING, "style": "bold yellow"},
    "error": {"level": LogLevel.ERROR, "style": "bold red"},
    "exception": {"level": LogLevel.EXCEPTION, "style": "bold red"},
    "success": {"level": LogLevel.SUCCESS, "style": "bold green"},
    "failure": {"level": LogLevel.FAILURE, "style": "bold red underline"},
    "verbose": {"level": LogLevel.VERBOSE, "style": "bold blue"},
}

THEME_TO_RICH: dict[str, str] = {k: v["style"] for k, v in THEME.items()}  # type: ignore[arg-type]


@dynamic_methods(methods=THEME, delegate_to="_log")
class BasicLogger(TypeLogger):
    """A basic logger that uses the Rich library to print messages to the console."""

    def __init__(self, level: str | int | LogLevel = LogLevel.INFO, **kwargs) -> None:
        """Initialize the BasicLogger with a Rich Console instance.

        Args:
            level (str | int | LogLevel): The logging level for the logger.
            **kwargs: Additional keyword arguments for the Rich Console.
        """
        theme: dict = kwargs.pop("theme", THEME_TO_RICH)
        self.console = Console(theme=Theme(theme), **kwargs)
        self.level: LogLevel = LogLevel.get(level, LogLevel.INFO)

    def _log(self, msg: object, level: LogLevel, style: str, **kwargs) -> None:
        """Log a message at the specified level."""
        if level >= self.level:
            if level == LogLevel.EXCEPTION:
                self.console.print_exception()
            self.console.print(msg, style=style, **kwargs)

    def print(
        self,
        msg: object,
        step: str = " ",
        end: str = "\n",
        style: str | None = None,
        **kwargs,
    ) -> None:
        """Print a message to the console with the specified style.

        Args:
            msg (object): The message to print.
            step (str): The separator between messages.
            end (str): The end character after the message.
            style (str | None): The style to apply to the message.
            **kwargs: Additional keyword arguments for formatting.
        """
        self.console.print(msg, sep=step, end=end, style=style, **kwargs)

    def inspect(self, obj: object, all: bool = False, methods: bool = False, **kwargs) -> None:  # noqa: A002
        """Inspect an object and print its details to the console.

        Args:
            obj (object): The object to inspect.
            all (bool): Whether to show all attributes.
            methods (bool): Whether to include methods in the inspection.
            **kwargs: Additional keyword arguments for formatting.
        """
        inspect(obj, console=self.console, all=all, methods=methods, **kwargs)

    def print_json(self, data: object, indent: int = 2, **kwargs) -> None:
        """Print a JSON object to the console.

        Args:
            data (object): The JSON data to print.
            **kwargs: Additional keyword arguments for formatting.
        """
        self.console.print_json(data=data, indent=indent, **kwargs)
