# bear_dereth.files

File abstraction layer that powers the datastore, settings manager, and logging
components. It wraps common formats (JSON, TOML, YAML, XML, text) with unified
handlers, caching, and path utilities.

## Core Concepts
- `BaseFileHandler`: Common interface (context manager) for reading/writing
  structured data with optional file locking.
- Specific handlers live in subpackages (`jsonl/`, `jsons/`, `toml/`, `xmls/`,
  `yamls/`, `text/`, `msgpack/`). Each exposes a Pydantic-friendly API.
- `file_cache`: Lightweight cache for memoizing file contents.
- `file_lock.py`: Cross-platform advisory locking to guard concurrent writes.
- `textio_utility.py`: Convenience helpers (`stdout`, `stderr`, `NULL_FILE`) used
  by loggers and CLIs.
- `helpers.py`: Path helpers (derive settings paths, ensure suffixes, etc.).
- `file_info.py`: Introspects file metadata (size, timestamps, mimetype).
- `mock_text.py`: StringIO-backed text handler for tests.

---

## Basic Usage

```python
from funcy_bear.files.jsons.file_handler import JSONFileHandler

handler = JSONFileHandler(file="config.json", touch=True)

config = handler.read(default={})
config["theme"] = "midnight"
handler.write(config, indent=2)
```

Each handler supports:
- Context manager usage (`with JSONFileHandler(...) as fh: ...`)
- `read()` / `write()` methods that return native Python types
- Optional kwargs for formatting (indentation, encoding, etc.)
- `touch=True` to create missing files/directories

---

## Choosing a Handler

| Subpackage | Purpose                                                           |
| ---------- | ----------------------------------------------------------------- |
| `jsonl/`   | Line-delimited JSON; great for logs or WAL-style append-only data |
| `jsons/`   | Standard JSON file handling                                       |
| `toml/`    | TOML read/write (Tomli/Tomli-W under the hood)                    |
| `xmls/`    | XML parsing, building Elements with helper utilities              |
| `yamls/`   | YAML support via ruamel-safe helpers                              |
| `text/`    | Plain text, line-based operations                                 |
| `msgpack/` | Binary serialization using MessagePack                            |

Most handlers share a consistent API, so swapping formats is straightforward.

---

## Path & Cache Helpers

```python
from bear_dereth.files.helpers import derive_settings_path

path = derive_settings_path("bear-dereth", file_name="config.json")
```

- `derive_settings_path(...)` locates application settings folders (mirrors the
  config module’s behaviour).
- `file_cache` offers simple caching decorators and helpers for repeated reads.
- `file_info.FileInfo` wraps filesystem metadata for reporting/logging.

---

## Tips
- When piping into the datastore, use the matching handler (e.g.,
  `JSONLFilehandler`) to ensure append-mode writes and concurrency safety.
- `mock_text.MockText` is handy for tests—no real files touched.
- Combine with `file_lock.py` in multi-process contexts to avoid clobbers.
- Many handlers accept `touch=True` and `mkdir=True` so they create directories
  automatically—perfect for first-run setup scripts.

File it all away neatly, Bear! 🐻📁✨
