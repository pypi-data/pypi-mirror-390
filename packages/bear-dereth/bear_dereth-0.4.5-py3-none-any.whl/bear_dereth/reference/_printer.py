from __future__ import annotations

from typing import TYPE_CHECKING

from lazy_bear import LazyLoader

if TYPE_CHECKING:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.theme import Theme
else:
    Console = LazyLoader("rich.console").to("Console")
    Syntax = LazyLoader("rich.syntax").to("Syntax")
    Theme = LazyLoader("rich.theme").to("Theme")


def syntax_print(m: dict, title: str, lang: str = "python") -> None:
    console = Console(
        theme=Theme(
            {
                "header": "bold magenta",
                "section": "bold cyan",
                "example": "green",
            }
        )
    )
    console.print(f"# {title}", style="header")
    for section, content in m.items():
        console.print(f"\n## {section}", style="section")
        syntax = Syntax(content.strip(), lang, theme="monokai", line_numbers=False)
        console.print(syntax)
