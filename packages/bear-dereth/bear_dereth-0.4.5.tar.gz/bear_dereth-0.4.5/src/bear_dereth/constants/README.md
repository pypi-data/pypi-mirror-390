# bear_dereth.constants

Shared constants and enum helpers used across Bear Dereth for filesystem
paths, byte math, HTTP codes, and typed exception messages.

## Exports
- `PATH_TO_*`: Canonical paths for Downloads, Pictures, Documents, Home, and
  config directories. `PATH_TO_CONFIG` honors `XDG_CONFIG_HOME` or falls back to
  platform-specific defaults.
- `FILE_EXTS`, `IMAGE_EXTS`, `VIDEO_EXTS`: Handy extension whitelists for media
  detection.
- `FILE_SIZES`: Mapping of human-readable size names to byte multipliers, plus
  `Kilobytes`, `Megabytes`, `Gigabytes`, `Terabytes` helper classes that convert
  inputs to bytes on instantiation.
- `HTTPStatusCode`: Rich enum of common HTTP responses with descriptive text,
  alongside direct aliases like `SERVER_OK` and `PAGE_NOT_FOUND`.
- `ExitCode`: Lazy-loaded link to the CLI exit codes (keeps import costs down).

## Exceptions
`exceptions.py` centralizes custom errors used across modules:
- `ObjectTypeError`, `InputObjectError`, `OutputObjectError`: Type mismatch
  helpers that emit friendly messages.
- `CannotFindTypeError`, `CannotInstantiateObjectError`: Raised when DI or
  reflection cannot resolve a type or construct an instance.
- `UserCancelledError`, `UnexpectedStatusCodeError`, `HandlerNotFoundError`,
  `StateTransitionError`: Purpose-built signals for CLI and state-machine code.

## Binary Types

`binary_types.py` now bundles a full toolkit for ctypes-backed metadata:
- `MetaStruct` and `StructField`: metaclass + base class that expose format
  codes, bit-width, signedness, and min/max bounds for each ctypes field.
- Ready-made field classes (`UINT8Field`, `INT32Field`, `DoubleField`, etc.)
  that map to the underlying `ctypes` primitives.
- Convenience aliases (`UINT8`, `INT64`, `FLOAT_TYPE`, `BOOLEAN_TYPE`, …) for
  quick lookups when assembling `struct` format strings.
- `BITS_IN_BYTE` constant and tuple constants (e.g. `INT_TYPE`, `STRING_TYPE`)
  for schema validation and binary parsing helpers in `operations.binarystuffs`.

Great for describing binary layouts or auto-generating struct packing code.

## Usage Notes
- Use the size wrapper classes when you need compile-time clarity (`Megabytes(5)`
  is easier to read than `5 * 1024**2`).
- Since `ExitCode` is lazy-loaded, importing `bear_dereth.constants` won’t pull
  in the entire CLI stack until you touch it.
- If you add new file extensions or status codes, update the README and keep the
  re-export list in `__all__` aligned so static analyzers stay happy.

Keep your constants cuddly and consistent, Bear! 🐻📏✨
