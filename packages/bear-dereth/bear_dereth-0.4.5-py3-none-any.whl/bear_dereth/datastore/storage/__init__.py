"""Storage backends for the datastore."""

from ._base_storage import Storage
from ._dynamic_storage import StorageChoices, get_storage, storage_map
from .json import JsonStorage
from .jsonl import JSONLStorage
from .memory import InMemoryStorage
from .msgpack import MsgPackStorage
from .toml import TomlStorage
from .xml import XMLStorage
from .yaml import YamlStorage

__all__ = [
    "InMemoryStorage",
    "JSONLStorage",
    "JsonStorage",
    "MsgPackStorage",
    "Storage",
    "StorageChoices",
    "TomlStorage",
    "XMLStorage",
    "YamlStorage",
    "get_storage",
    "storage_map",
]
