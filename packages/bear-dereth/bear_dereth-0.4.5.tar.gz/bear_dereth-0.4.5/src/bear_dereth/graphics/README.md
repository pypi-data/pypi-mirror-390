# bear_dereth.graphics

Color gradients, ASCII fonts, and flashier console helpers for Bear Dereth’s
output layers. The package leans on `rich` for rendering and feeds higher-level
CLI widgets.

## Modules
- `bear_gradient.py`: Three-stop RGB gradient interpolation with threshold
  control.
- `font/`: ASCII font utilities, including block letters, glitch effects, and
  header builders.
  - `_theme.py`: Color + glyph enums (`CyberTheme`, `FontStyle`).
  - `block_font.py`: Bold block-letter rendering with style swapping.
  - `glitch_font.py`: Pseudo-random cyberpunk glitches.
  - `_utils.py`: Gradient-driven color pickers, rich-powered headers, optional
    Figlet integration.

---

## ColorGradient

`ColorGradient` maps scalar input to RGB triplets using configurable start,
mid, and end colors (default red → yellow → green). Thresholds determine where
each segment blends. Values outside the provided range clamp automatically.

```python
from bear_dereth.graphics.bear_gradient import ColorGradient

gradient = ColorGradient()
# Map CPU percentage into an ANSI RGB hex string
color = gradient.map_to_rgb(0.0, 100.0, current_usage)
# Or grab a Rich ColorTriplet directly
triplet = gradient.map_to_color(0.0, 100.0, current_usage)
```

Pass `reverse=True` or call `flip()` to invert the direction. Custom palettes
can be provided by subclassing `DefaultColorConfig` or swapping the Pydantic
models (`DefaultColors`, `DefaultThresholds`).

---

## Block Font Renderer

`font/block_font.py` ships with a lookup table for letters, digits, and a small
set of punctuation. Helpers stitch per-character ASCII art into multi-line
strings and optionally restyle the fill glyph via `FontStyle`.

```python
from bear_dereth.graphics.font import word_to_block, print_block_font

banner = word_to_block("BEAR", font="dotted")
print(banner)

print_block_font("DERETH", color="bright_magenta")
```

Key helpers:
- `char_to_block(char)`: Retrieve the raw five-row glyph.
- `word_to_block(text, font="solid")`: Return a newline-delimited string.
- `print_block_font(text, color=CyberTheme.neon_green)`: Emit centered Rich
  output using theme colors.

`FontStyle` enumerates available glyph substitutions (solid blocks, outlines,
arrows, stars, etc.) and integrates with Rich via `str(style)` or `style.text`.

---

## Glitch Fonts

`glitch_font.py` embraces chaos. The generator walks a string, inserts random
glyphs (`█ ▓ ░ ▒ …`) with configurable intensity, and returns the result:

```python
from bear_dereth.graphics.font.glitch_font import cyberpunk_glitch_font

title = cyberpunk_glitch_font("Signal Lost", style="corrupted")
print(title)
```

Use `multi_line_glitch` for stacked lines or `glitch_font_generator` when you
need precise control over intensity per character.

---

## Header & Styling Utilities

`font/_utils.py` bundles helpers for console headers:

```python
from bear_dereth.graphics.font._utils import TextHelper

helper = TextHelper()
helper.quick_header("Mission Briefing")
helper.print_header("Diagnostics", top_sep="=", bottom_sep="=", length=50)
```

- `TextHelper.print_header(...)` returns or prints Rich formatted separators.
- `TextHelper.quick_header(style=...)` ships with presets (`cyberpunk`,
  `panel`, `classic`, `minimal`).
- `random_style()` uses the gradient to select a color for dynamic demos.
- Optional `pyfiglet` integration unlocks fancy ASCII art fonts; the module
  auto-detects availability via `HAS_PYFIGLET`.

---

## Tips
- Stick to uppercase input for block letters—unsupported characters are
  filtered out.
- Combine `ColorGradient` with logging or progress bars for easy at-a-glance
  severity cues.
- When building Rich panels, reuse `CyberTheme` so colors stay consistent across
  tools.
- The modules rely on pseudo-randomness for styling; seed the `random` module or
  stub `os.urandom` in tests if you need deterministic output.

Enjoy the glow, Bear! 🎨✨
