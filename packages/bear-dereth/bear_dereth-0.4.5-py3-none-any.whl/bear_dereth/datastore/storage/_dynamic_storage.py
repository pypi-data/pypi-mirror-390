"""Dynamic storage backend registry.

THIS FILE IS AUTO-GENERATED - DO NOT EDIT MANUALLY
Run `bear-dereth sync-storage` to regenerate
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from bear_dereth.datastore.storage.json import JsonStorage
from bear_dereth.datastore.storage.jsonl import JSONLStorage
from bear_dereth.datastore.storage.memory import InMemoryStorage
from bear_dereth.datastore.storage.msgpack import MsgPackStorage
from bear_dereth.datastore.storage.toml import TomlStorage
from bear_dereth.datastore.storage.xml import XMLStorage
from bear_dereth.datastore.storage.yaml import YamlStorage

if TYPE_CHECKING:
    from bear_dereth.datastore.storage._base_storage import Storage

type StorageChoices = Literal["json", "jsonl", "memory", "msgpack", "toml", "xml", "yaml", "default"]

storage_map: dict[str, type[Storage]] = {
    "json": JsonStorage,
    "jsonl": JSONLStorage,
    "memory": InMemoryStorage,
    "msgpack": MsgPackStorage,
    "toml": TomlStorage,
    "xml": XMLStorage,
    "yaml": YamlStorage,
    "default": JSONLStorage,
}


@overload
def get_storage(storage: Literal["json"]) -> type[JsonStorage]: ...
@overload
def get_storage(storage: Literal["jsonl"]) -> type[JSONLStorage]: ...
@overload
def get_storage(storage: Literal["memory"]) -> type[InMemoryStorage]: ...
@overload
def get_storage(storage: Literal["msgpack"]) -> type[MsgPackStorage]: ...
@overload
def get_storage(storage: Literal["toml"]) -> type[TomlStorage]: ...
@overload
def get_storage(storage: Literal["xml"]) -> type[XMLStorage]: ...
@overload
def get_storage(storage: Literal["yaml"]) -> type[YamlStorage]: ...
@overload
def get_storage(storage: Literal["default"]) -> type[JSONLStorage]: ...
def get_storage(storage: StorageChoices = "default") -> type[Storage]:
    """Factory function to get a storage backend by name.

    Args:
        storage: Storage backend name

    Returns:
        Storage backend class
    """
    storage_type: type[Storage] = storage_map.get(storage, storage_map["default"])
    return storage_type


__all__ = ["StorageChoices", "get_storage", "storage_map"]
