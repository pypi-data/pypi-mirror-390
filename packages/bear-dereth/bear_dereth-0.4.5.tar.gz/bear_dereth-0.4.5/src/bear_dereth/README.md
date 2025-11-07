# bear_dereth package

Top-level helpers that glue the rest of the Bear Dereth toolkit together. Most
subpackages have their own README, but a handful of modules live at the root
for easy importing or because they’re shared across multiple subsystems.

## Entry Points
- `__init__.py`: Re-exports convenience shortcuts (e.g., `config` helpers).
- `__main__.py`: CLI entry (`python -m bear_dereth`) → delegates to
  `bear_dereth._internal.cli`.

## Utility Modules
- `add_methods.py`: Decorators for dynamically attaching methods to classes
  (used by loggers and other configurable components).
- `dynamic_meth.py`: Lower-level machinery for generating methods at runtime.
- `async_helpers.py`: Async-friendly wrappers (`run_sync`, `timeout`, etc.) used
  by queue handlers and other I/O-heavy modules.
- `platform_utils.py`: OS/architecture detection, default paths, shell helpers.
- `system_bools.py`: System capability probes (e.g., whether Rich color is
  enabled, running on Windows, etc.).
- `sentinels.py`: Shared sentinel objects (`EXIT_SIGNAL`, `NO_DEFAULT`, …) used
  across the codebase.

## Core Subpackages
Each subfolder has a dedicated README covering details:

- `cli/`: Typer/Rich command-line commands.
- `config/`: App configuration & settings manager.
- `constants/`: Shared constants and convenience enums.
- `data_structs/`: Immutable helpers, stacks/queues, WAL, and LRU caches.
- `datastore/`: Storage engine with JSON/TOML/etc. backends.
- `di/`: Dependency-injection container and wiring.
- `files/`: File handler abstractions (JSONL, text, YAML, etc.).
- `graphics/`: Rich/ASCII rendering utilities.
- `logger/`: Handler-based logging stack.
- `math/`: Interpolation helpers + infinity sentinel.
- `models/`: Pydantic models and type-safe fields.
- `operations/`: Functional helpers, table operations, random utilities.
- `query/`: TinyDB-style query DSL.
- `rich_enums/`: Metadata-rich enum implementations.
- `stringing/`: String manipulation, templates, casing.
- `typing_tools/`: Type inference, coercion, and introspection.
- `versioning/`: SemVer models and CLI helpers.
- `reference/`: Additional samples/demos (not part of the published API).

When in doubt, start with the package README inside each directory—this root
file just maps the landscape. Happy exploring, Bear! 🐻🗺️✨
