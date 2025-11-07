# bear_dereth.versioning

Helpers for inspecting and bumping package versions. These utilities wrap
semantic-version parsing, provide enum-backed part identifiers, and expose CLI
helpers for automated bumps.

## Modules
- `classes.py`: Core models (`Version`, `VersionParts`, `Parts`) with parsing
  and mutation helpers.
- `commands.py`: CLI-oriented helpers (`cli_bump`, `get_version`) that return
  exit codes and print results.
- `consts.py`: Shared constants and type aliases (`BumpType`,
  `VALID_BUMP_TYPES`).

---

## Version Model

`Version` is a Pydantic model with `major`, `minor`, `patch`, and optional
`post` segments. It can be constructed from strings, tuples, or metadata pulled
from installed packages.

```python
from bear_dereth.versioning import Version

v = Version.from_string("v1.4.2")
assert str(v) == "1.4.2"

v.new_version("minor")
assert str(v) == "1.5.0"
```

Key helpers:
- `Version.from_parts(Parts.split("1.2.3"))`: Accepts three-part or four-part
  versions (fourth is treated as `post`).
- `Version.from_meta("bear-dereth")`: Reads the installed package version via
  `importlib.metadata`.
- `Version.new_version(bump_type)`: Mutates the model in place, incrementing
  the requested part and zeroing lower-order parts.

`VersionParts` is a `RichIntEnum`, so you can call `VersionParts.get("minor")`
or iterate over parts with metadata intact.

---

## CLI Helpers

```python
from bear_dereth.versioning import cli_bump, get_version
from bear_dereth.cli import ExitCode

current = get_version("bear-dereth")
result = cli_bump("patch", package_name="bear-dereth", ver=current)
assert result is ExitCode.SUCCESS
```

- `get_version(package_name)` wraps the package metadata lookup; raises
  `ValueError` if nothing is found.
- `cli_bump(bump_type, package_name, ver)` accepts either a version string or a
  `(major, minor, patch)` tuple. It prints the bumped version and returns an
  `ExitCode`.
- `VALID_BUMP_TYPES` (and `BumpType`) enforce that only `major`, `minor`, or
  `patch` are accepted.

---

## Tips
- When parsing user-supplied version strings, strip tags like `v1.2.3-rc1` via
  `Version.from_string`; it automatically trims `v` prefixes, pre-release, and
  build metadata.
- Use `Parts.split(...)` when you need to inspect segments without committing
  to a `Version` instance immediately.
- For automated release tooling, prefer `cli_bump` so exit codes integrate with
  scripts and CI.

Keep your versions marching forward, Bear! 🐻🔢✨
