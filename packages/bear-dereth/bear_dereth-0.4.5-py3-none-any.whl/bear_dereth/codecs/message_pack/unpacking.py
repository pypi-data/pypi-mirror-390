"""MessagePack unpacking functionality."""

from io import BytesIO
from typing import Any

from funcy_bear.files.text.bytes_handler import BytesFileHandler

from bear_dereth.codecs.message_pack._unpacking import unpack_one


def unpack(data: bytes) -> Any:
    """Unpack MessagePack bytes into a Python object."""
    buf = BytesFileHandler(buffer=BytesIO(data))
    return unpack_one(buf)
