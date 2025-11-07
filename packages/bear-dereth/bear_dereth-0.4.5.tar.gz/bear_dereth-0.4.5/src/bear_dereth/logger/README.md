# bear_dereth.logger

Rich-powered logging with configurable themes, DI-driven setup, and multiple
handlers. The package ships with a full-featured `BearLogger` plus lightweight
fallbacks (`BasicLogger`, `SimpleLogger`) when you just need quick console
output.

## Primary APIs
- `BearLogger`: Rich-enabled logger that supports multiple handlers, queueing,
  dynamic style methods, and `LoggerRecord` payloads.
- `BasicLogger` / `SimpleLogger`: Minimal console loggers without the DI layer.
- `LoggerConfig`: Pydantic configuration model (root settings, handler
  overrides, themes).
- Handlers (`ConsoleHandler`, `FileHandler`, `BufferHandler`, `QueueHandler`) +
  `QueueListener` for async fan-out.
- `LogLevel`: Enum with additional levels (`SUCCESS`, `FAILURE`, `VERBOSE`,
  etc.).
- DI container (`Container`, `container`) that wires config, themes, and error
  callbacks via `bear_dereth.di`.

Everything above is exported from `bear_dereth.logger`.

---

## Quick Start (BearLogger)

```python
from bear_dereth.logger import BearLogger, LogLevel
from bear_dereth.logger.handlers import ConsoleHandler, BufferHandler

logger = BearLogger(
    name="demo",
    level=LogLevel.INFO,
    handlers=[
        ConsoleHandler(),        # writes to stdout/stderr
        BufferHandler(),         # keeps recent messages in memory
    ],
)

logger.info("Hello, Bear!")
logger.warning("Careful out there…")
```

Key features:
- Uses DI to pull `LoggerConfig`, console options, and theme definitions.
- Auto-generates methods for each theme key (e.g., `logger.success(...)`,
  `logger.exception(...)`).
- Emits `LoggerRecord`s to each handler; records include stack info, timestamp,
  style, and structured metadata.
- `print_exception()` renders a Rich traceback to an internal buffer and returns
  the text (used by `exc_info=True`).

Configuration resolution looks in `~/.config/bear_dereth/logger/default.*` and
`./config/bear_dereth/logger/default.*` (matching `ConfigManager` behaviour).

---

## Basic & Simple Loggers

```python
from bear_dereth.logger import BasicLogger, SimpleLogger

basic = BasicLogger(level="info")
basic.info("Lightweight logging with Rich")

simple = SimpleLogger()
simple.error("Plain text logging with timestamps", extra={"user": "bear"})
```

- `BasicLogger` uses Rich with a static theme and dynamic helper methods
  (`info`, `debug`, `success`, etc.).
- `SimpleLogger` extends `BaseLogger`, writing to stdout/stderr (or any file
  handle) with optional buffering and timestamp formatting. Great fallback when
  the DI container isn’t available yet (e.g., init scripts).

---

## Handlers & Formatters

- `ConsoleHandler`: Rich console output; honours config overrides, respects
  handler-level thresholds, and uses `TemplateFormatter`.
- `FileHandler`: Rotating file support (size/rotation count derived from
  config). Writes formatted strings to disk.
- `BufferHandler`: Keeps formatted log strings in memory (useful for tests or
  in-process dashboards).
- `QueueHandler`: Pushes `LoggerRecord`s onto a queue; `QueueListener`
  processes records on background threads, forwarding to target handlers.
- `TemplateFormatter`: Wraps `string.Template` for `$variable` placeholders.
  Leveraged by default with templates from `LoggerConfig.formatter`.

All handlers accept `LogLevel` thresholds, optional custom formatters, and
error callbacks (defaults to `ErrorHandler`, which logs via `SimpleLogger`).

---

## Configuration Overview

`LoggerConfig` bundles several Pydantic models:
- `root`: Global level, default format, console overrides.
- `console`, `file`, `queue`: Per-handler enabling, formats, and overrides.
- `formatter`: Console/file/JSON templates, date formatting, stack trace options.
- `theme`: Style names that drive dynamic methods on `BearLogger`.

You can supply a custom config by building one in code or pointing the config
manager at another directory:

```python
from bear_dereth.logger.config import LoggerConfig
from bear_dereth.logger import BearLogger

config = LoggerConfig()
config.console.disable = False
config.file.disable = True

logger = BearLogger(config=config)
```

---

## Integrating With DI

```python
from bear_dereth.logger.config.di import Container, get_container
from bear_dereth.di import Provide

container = get_container()
Provide.set_container(Container)

logger = BearLogger()  # picks up injected config/theme/error handler
```

The container provides:
- `config_manager`: `ConfigManager[LoggerConfig]`
- `config`: Loaded `LoggerConfig`
- `custom_theme`, `console_options`
- `root_level`, `error_callback`

Override by registering new resources/handlers before instantiating the logger.

---

## Tips
- Use `logger.flush()` / `logger.close()` to clean up handlers (especially file
  and queue listeners) before exiting.
- When `QueueHandler(start=True)` is used, call `listener.stop()` or rely on
  context management to join background threads.
- `LoggerRecord` is a Pydantic model—handy for serializing or piping logs to
  JSON/TOML stores via custom handlers.
- For quick experiments, stick to `BasicLogger`; migrate to `BearLogger` when
  you need multiple handlers or theme-driven styling.

Log loud, log proud, Bear! 🐻📣✨
