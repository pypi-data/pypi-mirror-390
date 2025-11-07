"""MessagePack packing and unpacking handler with reusable buffer."""

from __future__ import annotations

from contextlib import suppress
from io import BytesIO
from typing import IO, Any, Self

from funcy_bear.files.text.bytes_handler import BytesFileHandler

from bear_dereth.codecs.message_pack._packing import pack_into
from bear_dereth.codecs.message_pack.unpacking import unpack_one


class MsgPackHandler:
    """In-memory cache for packing and unpacking MessagePack data.

    Maintains a reusable buffer for efficient serialization/deserialization.
    """

    def __init__(self, data: Any | None = None, buffer: type[IO] | IO | None = None) -> None:
        """Initialize the MsgPackHandler.

        Args:
            data: Initial data to load into the buffer (optional)
            buffer: In-memory buffer or buffer type (default: None)
        """
        from inspect import isclass  # noqa: PLC0415

        if buffer is None:
            buffer = BytesIO(data) if data is not None else BytesIO
        elif data is not None and isclass(buffer):
            buffer = buffer(data)  # type: ignore[arg-type]

        buffer = BytesIO(data) if data is not None and isclass(buffer) else buffer
        self.buffer = BytesFileHandler(buffer=buffer, append=True)

    def pack_into(self, x: object) -> None:
        """Pack an object into the buffer (accumulates data).

        Args:
            x: The object to pack into MessagePack format
        """
        pack_into(obj=x, buf=self.buffer)

    def pack(self, obj: Any) -> bytes:
        """Pack an object and return MessagePack bytes (clears buffer first).

        Args:
            obj: The object to pack into MessagePack format
        Returns:
            The packed MessagePack bytes
        """
        self.clear()
        self.buffer.offset_to_0()
        pack_into(obj=obj, buf=self.buffer)
        self.buffer.offset_to_0()
        return self.buffer.read()

    def unpack(self, data: bytes) -> Any:
        """Unpack MessagePack bytes into a Python object (from start of buffer).

        Args:
            data: The MessagePack bytes to unpack
        Returns:
            The unpacked Python object
        """
        self.clear()
        self.buffer.write(data, reset=True)
        result: Any = unpack_one(self.buffer)
        self.buffer.offset_to_0()
        return result

    def unpack_stream(self, data: bytes) -> Any:
        """Unpack the next MessagePack object from the current buffer position."""
        self.clear()
        self.buffer.write(data, reset=True)
        results: list[Any] = []
        with suppress(Exception):
            while self.buffer.get_offset() < len(data):
                result: Any = unpack_one(self.buffer)
                results.append(result)
        return results

    def clear(self) -> None:
        """Clear the internal buffer."""
        self.buffer.clear(offset=0)

    def get_buffer(self, clear: bool = False) -> bytes:
        """Get the current buffer contents as bytes."""
        current_offset: int = self.buffer.get_offset()
        self.buffer.offset_to_0()
        data: bytes = self.buffer.read()
        self.buffer.to_offset(current_offset)
        if clear:
            self.clear()
        return data

    @property
    def size(self) -> int:
        """Get the current size of the internal buffer."""
        return len(self.get_buffer())

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.clear()
