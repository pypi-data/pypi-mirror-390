# bear_dereth.models

Typed Pydantic helpers used throughout Bear Dereth for immutable configs,
secure fields, dynamic responses, XML generation, and more.

## Overview
- `general.py`: Base classes like `FrozenModel` (immutable) and
  `ExtraIgnoreModel`.
- `type_fields.py`: Root models for secrets, passwords, tokens, filesystem
  paths, and lightweight numeric annotations (`PositiveInt`).
- `function_response.py`: Rich response wrapper that aggregates stdout/stderr,
  sub-tasks, and dynamic attributes.
- `helpers.py`: Utilities such as `DynamicAttrs`, `nullable_string_validator`,
  and `extract_field_attrs`.
- `meta_path.py`: `WrappedPath` for serializing paths with metadata.
- `xml_base_element.py`: Base classes for building XML trees with Pydantic.
- `corrective_factors.py`: RGB helper (`RGBValues`) for computing color
  correction factors.
- `general.py`, `function_response.py`, and `type_fields.py` are re-exported in
  `bear_dereth.models.__init__`.

---

## Secure & Path Fields

```python
from bear_dereth.models import SecretModel, PathModel, TokenModel

secret = SecretModel.load("hunter2")
assert secret.is_null() is False
assert str(secret) == "****"

cfg_dir = PathModel("~/.config/bear-dereth")
assert cfg_dir().name == "bear-dereth"

token = TokenModel.load("abc123")
print(token.get_secret_value())  # safe access when needed
```

- `SecretModel` treats placeholder strings like `"null"`/`"****"` as empty and
  hides values when serialized.
- `PathModel` normalizes paths (`expanduser`, `resolve`) and proxies attribute
  access to the underlying `Path`.

`PositiveInt` (a `typing.Annotated[int]`) is used in models that expect
non-negative, sub-1000 integers (e.g., version parts, return codes).

---

## FunctionResponse

`FunctionResponse` captures outcomes from commands or sub-tasks—think of it as
a structured return object with logging hooks.

```python
from subprocess import CompletedProcess
from bear_dereth.models.function_response import FunctionResponse

proc = CompletedProcess(args=["echo", "Bear"], returncode=0, stdout="Bear\n", stderr="")
res = FunctionResponse.from_process(proc).successful("All good!")

assert res.success is True
assert res.content_number == 2

sub = res.sub_task(name="cleanup", content="done")
payload = sub.done(to_dict=True)
```

- `.add(...)` handles raw strings, lists, nested `FunctionResponse`, or
  `CompletedProcess` instances.
- `.sub_task(...)` nests additional responses and keeps them accessible via
  `res.sub_tasks`.
- `.done(to_dict=True)` returns a filtered dict suitable for logging/JSON.

`DynamicAttrs` underpins the dynamic property system, letting you assign new
fields (`res.duration_ms = 42`) without breaking validation.

---

## Path Metadata

`WrappedPath` augments `Path` objects with useful metadata for APIs/UI layers:

```python
from bear_dereth.models.meta_path import WrappedPath

meta = WrappedPath(path="README.md")
print(meta.name, meta.suffix, meta.exists)
print(meta.parent)  # dict of parent -> WrappedPath
```

It calculates existence flags, timestamps (via `bear_epoch_time`), file size,
URI, and parent hierarchy during `model_post_init`. The model is geared toward
external integrations—pass a single serialized payload across process
boundaries or to CLIs without forcing consumers to reconstruct `Path` logic,
while Python code can still use plain `Path` when richer objects aren’t needed.

---

## XML Elements

`BaseElement` provides a Pydantic-backed way to build XML trees:

```python
from bear_dereth.models.xml_base_element import BaseElement

class Project(BaseElement):
    tag = "project"
    name: str

project = Project(name="Bear")
xml_string = project.to_string()
```

- `add(sub_element)` appends child elements.
- `get(...)` / `has_element(...)` let you query sub-elements by tag or type.
- Serialization auto-converts numeric/bool fields to strings per XML norms.
You can build layered schemas by composing subclasses (e.g., a `<database>`
element that adds `<tables>` children). Each subclass keeps type hints for its
fields and nested elements, so editors understand the XML hierarchy while the
runtime still emits plain `ElementTree` nodes.

Check `src/bear_dereth/datastore/adapter/xml/schemas.py` for a real-world usage
pattern: concrete subclasses map onto datastore XML structures while keeping
static typing and editor hints crisp.

---

## Color Correction

`RGBValues` normalizes raw RGB channels to compute correction factors:

```python
from bear_dereth.models.corrective_factors import RGBValues

rgb = RGBValues(r_=128, g_=255, b_=64)
print(rgb.to_string())         # CorrectiveFactors(r=1.99..., g=1.0, b=3.98...)
print(rgb.to_string(raw=True)) # RawRGB(r=128, g=255, b=64)
```

Validation ensures values stay within `0-255`, and computed fields expose both
normalized and factor forms.

---

## Extras & Helpers
- `nullable_string_validator("field")` quickly converts `"null"`/`""` to `None`
  in your own models.
- `extract_field_attrs(SomeModel, dict, attr="json_schema_extra")` pulls custom
  field attributes into a dictionary.

Keep your models tidy and type-safe, Bear! 🐻📦✨
