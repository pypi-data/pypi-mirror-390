# bear_dereth.config

Utilities for loading structured application configuration, managing on-disk settings, and resolving project directory locations. The module ties together typed Pydantic models, the BearBase datastore, and helper functions for durable storage.

## Components At A Glance
- `ConfigManager`: Merge layered TOML files and environment variables into a typed Pydantic model.
- `DirectoryManager`: Resolve standard directories (`~/.config`, project `./config`, cache, temp) with optional auto-creation.
- `BearSettings` / `SettingsManager`: Persistent key-value store backed by `bear_dereth.datastore.BearBase`.
- `BaseSettingHandler`: Thin wrapper that wires a `BearSettings` instance into dedicated tables for domain-specific settings.
- `SimpleSettingsManager`: Lightweight file-based settings helper (JSON/YAML/TOML) without the datastore dependency.

The package also exports convenience functions such as `get_config_path`, `get_settings_path`, and `clear_temp_directory`.

---

## ConfigManager

`ConfigManager[ConfigType]` accepts a Pydantic model and merges configuration sources in a predictable order. It normalizes the program name (slug → upper snake-case) to derive environment variable prefixes and directory names.

```python
from pydantic import BaseModel
from bear_dereth.config import ConfigManager

class AppConfig(BaseModel):
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000

config_manager = ConfigManager[AppConfig](
    config_model=AppConfig,
    program_name="Bear Dereth",
    env="prod",
)

config = config_manager.config
print(config.host, config.port)
```

**Merge precedence (later wins):**
1. `default.toml`
2. `{env}.toml` (e.g. `prod.toml`)
3. `local.toml`
4. Environment variables beginning with the slugified prefix (e.g. `BEAR_DERETH_DATABASE_HOST`).

**Search locations:**
- `~/.config/<program_name>/`
- `./config/<program_name>/` (relative to the current working directory)
- Any additional absolute paths supplied via `config_paths`.

Environment variable parsing performs light type coercion (bool/int/float/list) when possible. Use the `Sources` helper (`config_manager.config_sources()`) to inspect which files were loaded, which paths were scanned, and which env vars were applied during debugging.

Additional capabilities:
- `reload()` invalidates cached properties so new files/env vars are pulled in.
- `create_default_config()` writes a TOML file populated from the current model state.
- `has_config(SomeSubModel)` / `get_config(SomeSubModel)` allow feature detection for embedded models without hand-parsing.

---

## DirectoryManager

`DirectoryManager` wraps common filesystem locations and mirrors the XDG-style layout used across the project. Every accessor accepts `mkdir=True` to ensure the directory exists before returning.

```python
from bear_dereth.config import DirectoryManager, get_cache_path

dirs = DirectoryManager("bear-dereth")
cache_dir = dirs.cache_path(mkdir=True)          # ~/.cache/bear-dereth
project_cfg = dirs.local_config(mkdir=True)      # ./config/bear-dereth

# Helper functions simply instantiate the manager internally:
settings_dir = get_settings_path("bear-dereth", mkdir=True)
```

Custom directories can be registered via `dirs.register("artifacts", Path("/tmp/artifacts"), mkdir=True)` and accessed as attributes or dictionary-style (`dirs.artifacts` / `dirs["artifacts"]`).

---

## Persistent Settings (BearSettings / SettingsManager)

`BearSettings` is a durable key-value store built on top of `bear_dereth.datastore.BearBase`. Data is stored in tables described by `SettingsModel`, enabling schema-aware reads and writes across multiple storage engines:

```python
from bear_dereth.config import SettingsManager

settings = SettingsManager(
    name="bear-dereth",
    storage="jsonl",   # json (default), jsonl, toml, yaml, xml, memory
)

settings.set("theme", "midnight")
settings.set("beta", True)
settings.set("timeout", 30, as_type="int")

assert settings.get("theme") == "midnight"
```

Key features:
- Storage backends come from `bear_dereth.datastore.storage`; `StorageChoices` is a literal type ensuring only supported engines are used.
- Values are upserted into a dedicated settings table (`SettingsModel`) so metadata such as type hints are preserved alongside the stored value.
- Type casting happens on read via `typing_tools.str_to_bool` and `str_to_type`, with a custom map for additional coercions (e.g. epoch timestamps).
- Dot-style access (`settings.theme`) and mapping semantics (`settings["theme"]`) are forwarded to the underlying datastore.
- The context manager (`with settings(...) as sm:`) guarantees the BearBase connection is closed.

Retrieving more advanced views:

```python
from bear_dereth.config.settings_db_cls import SettingsModel

for key, value in settings.items():
    print(key, value)

table = settings.table                   # raw BearBase table
records = table.all()                    # list of Record instances
columns = SettingsModel.get_columns()    # schema exported by the model
```

---

## BaseSettingHandler

`BaseSettingHandler` streamlines scenarios where a service needs to orchestrate multiple settings tables while retaining backup copies of the underlying storage file.

```python
from bear_dereth.config import BaseSettingHandler
from bear_dereth.config.settings_db_cls import SettingsModel

handler = BaseSettingHandler("bear-dereth")
handler.register_table("feature_flags", SettingsModel)

handler.settings.set("show_beta_banner", True)
handler.feature_flags.set("new-parser", True)
```

- On initialization, the handler creates a `.backup` copy of the settings file if one does not already exist.
- Each registered table is wrapped in a `TableWrapper` exposing `get`, `set`, `delete`, `keys`, `values`, and `items`.
- Lookups internally rely on the datastore query system (`bear_dereth.query.where`) so applications can migrate to richer queries without rewriting domain logic.

This class is especially useful for services that need to coordinate different projections (e.g. `settings`, `secrets`, `feature_flags`) against a single persisted file.

---

## SimpleSettingsManager

For cases where the full datastore stack is unnecessary, `SimpleSettingsManager` offers a minimal API that reads/writes dictionaries using the project file handlers:

```python
from bear_dereth.config import SimpleSettingsManager

with SimpleSettingsManager("bear-dereth", fmt="yaml") as simple:
    simple.set("color", "lavender")
    assert simple.get("color") == "lavender"
```

- Supports JSON (`default`), YAML, and TOML files.
- File format is auto-detected from the supplied `file_name` extension, or can be forced via the `fmt` argument.
- Paths are resolved with `bear_dereth.files.helpers.derive_settings_path`, so custom directories and filenames mirror the behavior of `BearSettings`.

This helper keeps no long-lived handles open—the manager reads on construction and writes on mutation.

---

## Working With The Datastore Layer

Every settings API ultimately uses the abstractions within `src/bear_dereth/datastore`:
- `BearBase`: Lightweight document database with table support.
- `StorageChoices` & `get_storage()`: Factory for selecting storage engines (`json`, `jsonl`, `toml`, `yaml`, `xml`, `memory`).
- `Record`, `Table`, `Columns`: Building blocks for schema management and query execution.

Understanding these pieces is useful when you need to declare custom models (`SettingsModel` clones), register additional tables, or plug settings into other BearBase-powered components.

---

## Tips & Best Practices
- Keep TOML config files small and environment-specific; reserve `local.toml` for developer overrides ignored by Git.
- Use `ConfigManager.config_sources()` in tests to assert which files/environments were consulted.
- Prefer `SettingsManager` for multi-process or tool-driven settings, and `SimpleSettingsManager` for quick scripting or fixtures.
- Always call `mkdir=True` when you expect a directory to exist—helpers intentionally avoid creating folders by default.
- When introducing new settings tables, reuse `SettingsModel.get_columns()` so the datastore schema stays consistent.

Happy configuring, Bear! 🐻✨
