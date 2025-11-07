"""MessagePack packing entry point."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from funcy_bear.files.text.bytes_handler import BytesFileHandler

from bear_dereth.codecs.message_pack._packing import pack_into


def pack(obj: Any) -> bytes:
    """Pack an object into MessagePack bytes."""
    buf = BytesFileHandler(buffer=BytesIO, append=True)
    pack_into(obj=obj, buf=buf)
    return buf.read()
