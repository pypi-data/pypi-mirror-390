"""A file that will generate _dynamic_storage.py when run, allowing for faster plugin discovery.

The dynamic file will obviously have the imports for the storage using the absolute python path.
ie:
    from bear_dereth.datastore.storage.json import JsonStorage
    from bear_dereth.datastore.storage.msgpack import MsgPackStorage
    ...

It will add the value to the StorageChoices literal as seen here: Literal["jsonl", "toml", "yaml", "xml", "memory", "json", "msgpack", "default"]

It will then add the storage to the storage_map dict as such:
storage_map: dict[str, type[Storage]] = {
    "jsonl": JSONLStorage,
    "toml": TomlStorage,
    ...
}

Finally, it will add the necessary overloads for the get_storage function.
"""

from __future__ import annotations

from contextlib import suppress
from importlib import import_module
import inspect
from pathlib import Path
import pkgutil
from typing import TYPE_CHECKING, Final

from bear_dereth.cli.commands import RuffCommand as Ruff
from bear_dereth.cli.shell._base_shell import SimpleShellSession
from bear_dereth.logger.basic_logger import BasicLogger

if TYPE_CHECKING:
    from types import ModuleType

STORAGE_DIR: Path = Path(__file__).parent
OUTPUT_FILE: Path = STORAGE_DIR / "_dynamic_storage.py"
DEFAULT_BACKEND: Final[str] = "jsonl"

TRIPLE_QUOTE: Final[str] = '"""'
NEWLINE: Final[str] = "\n"
CLOSE_BRACE: Final[str] = "}"
INDENT: Final[str] = "    "
INDENT_2: Final[str] = INDENT * 2

ALL_LINE: Final[str] = '__all__ = ["StorageChoices", "get_storage", "storage_map"]'
IMPORT_BASE = "from bear_dereth.datastore.storage._base_storage import Storage"
IMPORT_LINE: Final[str] = "from bear_dereth.datastore.storage.{module_name} import {class_name}"
STORAGE_CHOICES = 'type StorageChoices = Literal["{literal_values}"]'
STORAGE_MAP_HEADER = "storage_map: dict[str, type[Storage]] = {"
OVERLOAD: Final[str] = "@overload"
OVERLOAD_DEF: Final[str] = 'def get_storage(storage: Literal["{key}"]) -> type[{class_name}]: ...'
IF_TYPE_CHECKING: Final[str] = "if TYPE_CHECKING:"
RUFF_CONFIG = "--config config/ruff.toml"


def discover_storage_backends() -> dict[str, tuple[str, str]]:
    """Scan storage directory for Storage subclasses.

    Returns:
        Dict mapping storage key to (class_name, module_name) tuple.
    """
    import bear_dereth.datastore.storage as storage_pkg
    from bear_dereth.datastore.storage._base_storage import Storage

    backends: dict[str, tuple[str, str]] = {}

    for _, modname, _ in pkgutil.iter_modules(storage_pkg.__path__):
        if modname.startswith("_"):
            continue
        with suppress(ModuleNotFoundError):
            module: ModuleType = import_module(f"bear_dereth.datastore.storage.{modname}")

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Storage) and obj is not Storage:
                    key: str = modname
                    backends[key] = (name, modname)
                    break
    return backends


def import_lines(lines: list[str], backends: dict[str, tuple[str, str]]) -> None:
    """Generate import lines for the dynamic storage file."""
    for _, (class_name, module_name) in backends.items():
        lines.append(IMPORT_LINE.format(module_name=module_name, class_name=class_name))
    lines.append(NEWLINE)
    lines.append(IF_TYPE_CHECKING)
    lines.append(INDENT + IMPORT_BASE)
    lines.append(NEWLINE)


def storage_choices(lines: list[str], backends: dict[str, tuple[str, str]]) -> None:
    """Generate the StorageChoices literal definition."""
    storage_keys: list[str] = [*list(backends.keys()), "default"]
    literal_values: str = '", "'.join(storage_keys)
    lines.append(STORAGE_CHOICES.format(literal_values=literal_values))
    lines.append(NEWLINE)


def storage_map(lines: list[str], backends: dict[str, tuple[str, str]]) -> str:
    """Generate the storage_map section of the dynamic storage file."""
    lines.append(STORAGE_MAP_HEADER)
    for key, (class_name, _) in backends.items():
        lines.append(f'{INDENT}"{key}": {class_name},')
    default_backend: str = backends.get(DEFAULT_BACKEND, next(iter(backends.values())))[0]
    lines.append(f'{INDENT}"default": {default_backend},')
    lines.append(CLOSE_BRACE)
    return default_backend


def overloads(lines: list[str], backends: dict[str, tuple[str, str]], default_backend: str) -> None:
    """Generate the overloads for the get_storage function."""
    for key, (class_name, _) in backends.items():
        lines.append(OVERLOAD)
        lines.append(OVERLOAD_DEF.format(key=key, class_name=class_name))
    lines.append(OVERLOAD)
    lines.append(OVERLOAD_DEF.format(key="default", class_name=default_backend))


def generate_storage_file() -> None:
    """Generate _dynamic_storage.py with auto-discovered storage backends."""
    backends: dict[str, tuple[str, str]] = discover_storage_backends()
    sorted_backends: dict[str, tuple[str, str]] = dict(sorted(backends.items()))
    lines: list[str] = [
        f"{TRIPLE_QUOTE}Dynamic storage backend registry.",
        NEWLINE,
        "THIS FILE IS AUTO-GENERATED - DO NOT EDIT MANUALLY",
        "Run `bear-dereth sync-storage` to regenerate",
        TRIPLE_QUOTE,
        NEWLINE,
        "from __future__ import annotations",
        NEWLINE,
        "from typing import Literal, overload, TYPE_CHECKING",
        NEWLINE,
    ]

    import_lines(lines, sorted_backends)
    storage_choices(lines, sorted_backends)
    default_backend: str = storage_map(lines, sorted_backends)
    overloads(lines, sorted_backends, default_backend)

    lines.extend(
        [
            'def get_storage(storage: StorageChoices = "default") -> type[Storage]:',
            f'{INDENT}"""Factory function to get a storage backend by name.',
            INDENT,
            f"{INDENT}Args:",
            f"{INDENT_2}storage: Storage backend name",
            INDENT,
            f"{INDENT}Returns:",
            f"{INDENT_2}Storage backend class",
            f"{INDENT}{TRIPLE_QUOTE}",
            f'{INDENT}storage_type: type[Storage] = storage_map.get(storage, storage_map["default"])',
            f"{INDENT}return storage_type",
            NEWLINE,
            NEWLINE,
            ALL_LINE,
            NEWLINE,
        ]
    )
    output: str = "\n".join(lines).replace("\n\n", "\n")
    OUTPUT_FILE.write_text(output)
    logger = BasicLogger()
    str_path = str(OUTPUT_FILE.relative_to(Path.cwd()))
    shell = SimpleShellSession(logger=logger, verbose=False)
    shell.add(Ruff(f"format {str_path} {RUFF_CONFIG}")).piped(Ruff(f"check {str_path} --fix {RUFF_CONFIG}")).run()
    logger.print(f"😎 {shell.stdout.strip()}", style="bold green")
    logger.print(f"✅ Generated [blue]{str_path}[/blue]", style="bold green")
    storage_keys: str = ", ".join(sorted_backends.keys())
    logger.print(f"📦 Discovered {len(sorted_backends)} storage backends: [blue]{storage_keys}[/blue]", style="green")


# ruff: noqa: PLC0415
