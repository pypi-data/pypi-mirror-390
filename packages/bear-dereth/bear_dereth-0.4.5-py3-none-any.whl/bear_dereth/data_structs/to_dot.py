"""Provide dot notation access to nested dictionaries."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Self, overload

from lazy_bear import LazyLoader

if TYPE_CHECKING:
    from collections.abc import Iterator
    import copy
    import json as _json

    from funcy_bear.api import LitFalse, LitTrue
    from funcy_bear.tools import freeze
else:
    _json = LazyLoader("json")
    copy = LazyLoader("copy")
    freeze = LazyLoader("funcy_bear.tools").to("freeze")


class DotDict(MutableMapping):
    """A dictionary that supports dot notation access to nested dictionaries.

    Example:
        >>> d = DotDict({"a": {"b": {"c": 1}}})
        >>> d.a.b.c
        1
        >>> d["a"]["b"]["c"]
        1
        >>> d.a.b.c = 2
        >>> d.a.b.c
        2
        >>> d["a"]["b"]["c"]
        2
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """Initialize the DotDict with an optional dictionary."""
        self._data: OrderedDict[str, Any] = OrderedDict()
        for key, value in (data or {}).items():
            if isinstance(value, dict):
                self._data[key] = DotDict(value)
            else:
                self._data[key] = value

    def __copy__(self) -> DotDict:
        """Return a shallow copy of the DotDict."""
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> DotDict:
        """Return a deep copy of the DotDict."""
        if memo is None:
            memo = {}
        copied_data = copy.deepcopy(self._data, memo)
        return DotDict(copied_data)

    def copy(self) -> DotDict:
        """Return a shallow copy of the DotDict."""
        return DotDict(self.as_dict())

    @overload
    def as_dict(self, json: LitFalse = False, indent: int = 4, sort_keys: bool = False) -> dict[str, Any]: ...
    @overload
    def as_dict(self, json: LitTrue, indent: int = 4, sort_keys: bool = False) -> str: ...

    def as_dict(self, json: bool = False, indent: int = 4, sort_keys: bool = False) -> dict[str, Any] | str:
        """Return a standard dictionary representation of the DotDict."""

        def convert(value: Any) -> Any:
            if isinstance(value, DotDict):
                return {k: convert(v) for k, v in value._data.items()}
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            return value

        result: dict[str, Any] = {k: convert(v) for k, v in self._data.items()}
        if json:
            return _json.dumps(result, indent=indent, sort_keys=sort_keys)
        return result

    def freeze(self) -> dict[str, Any]:
        """Return a frozen (immutable) version of the dictionary."""
        return freeze(self.as_dict())

    @classmethod
    def to_dot(cls, data: dict[str, Any]) -> Self:
        """Convert a standard dictionary to a DotDict."""
        dot: Self = cls()
        for key, value in data.items():
            if isinstance(value, dict):
                dot._data[key] = cls.to_dot(value)
            else:
                dot._data[key] = value
        return dot

    def __getattr__(self, key: str) -> Any:
        """Get an item using dot notation."""
        try:
            value = self._data[key]
            if isinstance(value, dict):
                return DotDict(value)
            return value
        except KeyError as e:
            raise AttributeError(f"'DotDict' object has no attribute '{key}'") from e

    def __setattr__(self, key: str, value: Any) -> None:
        """Set an item using dot notation."""
        if key == "_data":
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    def __delattr__(self, key: str) -> None:
        """Delete an item using dot notation."""
        try:
            del self._data[key]
        except KeyError as e:
            raise AttributeError(f"'DotDict' object has no attribute '{key}'") from e

    def __getitem__(self, key: str) -> Any:
        """Get an item using dictionary notation."""
        value = self._data[key]
        if isinstance(value, dict):
            return DotDict(value)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an item using dictionary notation."""
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete an item using dictionary notation."""
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the keys of the dictionary."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return the number of items in the dictionary."""
        return len(self._data)

    def __bool__(self) -> bool:
        """Return True if the DotDict is not empty."""
        return bool(self._data)

    def __repr__(self) -> str:
        """Return a string representation of the DotDict."""
        return f"DotDict({self.as_dict()})"


__all__ = ["DotDict"]
