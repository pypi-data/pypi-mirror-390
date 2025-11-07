"""Tests for MsgPackHandler class."""

from io import BytesIO
from typing import Any

from bear_dereth.codecs.message_pack.msg_pack_handler import MsgPackHandler
from bear_dereth.codecs.message_pack.packing import pack


class TestMsgPackHandler:
    """Test suite for MsgPackHandler."""

    def test_pack_unpack_dict(self):
        """Test packing and unpacking a dictionary."""
        handler = MsgPackHandler(data=None)
        data: dict[str, Any] = {"name": "Bear", "age": 42, "active": True}
        packed: bytes = handler.pack(data)
        unpacked: Any = handler.unpack(packed)
        assert unpacked == data

    def test_pack_unpack_list(self):
        """Test packing and unpacking a list."""
        handler = MsgPackHandler(data=None)
        data: list[int] = [1, 2, 3, 4, 5]
        packed: bytes = handler.pack(data)
        unpacked: Any = handler.unpack(packed)
        assert unpacked == data

    def test_pack_unpack_nested(self):
        """Test packing and unpacking nested structures."""
        handler = MsgPackHandler(data=None)
        data: dict[str, Any] = {
            "users": [
                {"id": 1, "name": "Bear"},
                {"id": 2, "name": "Claire"},
            ],
            "count": 2,
        }
        packed: bytes = handler.pack(data)
        unpacked: Any = handler.unpack(packed)
        assert unpacked == data

    def test_multiple_cycles(self):
        """Test multiple pack/unpack cycles with same handler."""
        handler = MsgPackHandler(data=None)

        # Cycle 1
        data1: dict[str, Any] = {"name": "Bear", "count": 42}
        packed1: bytes = handler.pack(data1)
        unpacked1: Any = handler.unpack(packed1)
        assert unpacked1 == data1

        # Cycle 2
        data2: list[int] = [1, 2, 3, 4, 5]
        packed2: bytes = handler.pack(data2)
        unpacked2: Any = handler.unpack(packed2)
        assert unpacked2 == data2

        # Cycle 3
        data3: dict[str, dict[str, dict[str, int]]] = {"nested": {"deep": {"value": 123}}}
        packed3: bytes = handler.pack(data3)
        unpacked3: Any = handler.unpack(packed3)
        assert unpacked3 == data3

    def test_pack_into(self):
        """Test pack_into method."""
        handler = MsgPackHandler(data=None)
        handler.pack_into({"test": 1})
        handler.pack_into([2, 3])
        buffer: bytes = handler.get_buffer()
        assert len(buffer) > 0

    def test_clear(self):
        """Test clear method."""
        handler = MsgPackHandler(data=None)
        handler.pack({"data": "test"})
        handler.clear()
        buffer: bytes = handler.get_buffer()
        assert len(buffer) == 0

    def test_get_buffer_clear(self):
        """Test get_buffer with clear=True."""
        handler = MsgPackHandler(data=None)
        handler.pack({"data": "test"})
        buffer1: bytes = handler.get_buffer(clear=False)
        assert len(buffer1) > 0
        buffer2: bytes = handler.get_buffer(clear=True)
        assert buffer1 == buffer2
        buffer3: bytes = handler.get_buffer()
        assert len(buffer3) == 0

    def test_pack_primitives(self):
        """Test packing various primitive types."""
        handler = MsgPackHandler(data=None)
        test_cases: list[Any] = [
            None,
            True,
            False,
            0,
            42,
            -1,
            3.14,
            "hello",
            b"bytes",
        ]
        for value in test_cases:
            packed: bytes = handler.pack(value)
            unpacked: Any = handler.unpack(packed)
            assert unpacked == value, f"Failed for {value!r}"

    def test_unpack_stream(self):
        """Test unpacking multiple objects from a stream."""
        handler = MsgPackHandler(data=None)
        obj1: dict[str, Any] = {"id": 1, "name": "Bear"}
        obj2: list[int] = [1, 2, 3]
        obj3 = "hello"
        packed: bytes = pack(obj1) + pack(obj2) + pack(obj3)
        results: Any = handler.unpack_stream(packed)
        assert len(results) == 3
        assert results[0] == obj1
        assert results[1] == obj2
        assert results[2] == obj3

    def test_size_property(self) -> None:
        """Test size property returns buffer length."""
        handler = MsgPackHandler(data=None)
        assert handler.size == 0
        data: dict[str, int] = {"test": 123}
        handler.pack(data)
        assert handler.size > 0
        handler.clear()
        assert handler.size == 0

    def test_context_manager(self) -> None:
        """Test context manager clears buffer on exit."""
        with MsgPackHandler(data=None) as handler:
            handler.pack({"data": "test"})
            assert handler.size > 0
        assert handler.size == 0

    def test_init_with_bytes_data(self) -> None:
        """Test initializing handler with bytes data."""
        data: dict[str, Any] = {"name": "Bear", "age": 42}
        packed: bytes = pack(data)
        handler = MsgPackHandler(data=packed)

        # Should be able to unpack without providing data again
        # (though our current API requires passing data to unpack)
        # This tests that init with data doesn't break anything
        handler.clear()
        unpacked: Any = handler.unpack(packed)
        assert unpacked == data

    def test_init_with_buffer_class(self) -> None:
        """Test initializing with buffer class and data."""
        data: dict[str, int] = {"test": 123}
        packed: bytes = pack(data)
        handler = MsgPackHandler(data=packed, buffer=BytesIO)
        handler.clear()
        unpacked: Any = handler.unpack(packed)
        assert unpacked == data

    def test_unpack_stream_single_object(self) -> None:
        """Test unpack_stream with single object."""
        handler = MsgPackHandler(data=None)
        data: dict[str, str] = {"single": "object"}
        packed: bytes = pack(data)
        results: Any = handler.unpack_stream(packed)
        assert len(results) == 1
        assert results[0] == data

    def test_unpack_stream_empty(self) -> None:
        """Test unpack_stream with empty data."""
        handler = MsgPackHandler(data=None)
        results: Any = handler.unpack_stream(b"")
        assert results == []
