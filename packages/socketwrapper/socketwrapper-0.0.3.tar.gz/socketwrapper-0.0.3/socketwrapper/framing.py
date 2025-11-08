"""Standard message framing implementations for socketwrapper."""

import abc
import collections.abc
import io
import os

from . import _varint, protocols


class MessageFramingBase[R, W](abc.ABC):
    """Base abstract class for message framing implementations."""

    @classmethod
    @abc.abstractmethod
    def frames(cls, buffer: io.BytesIO) -> collections.abc.Iterable[int]:
        """Get iterator with required read sizes."""

    @classmethod
    @abc.abstractmethod
    def loads(cls, buffer: io.BytesIO) -> R:
        """Get frame payload from full buffer."""

    @classmethod
    @abc.abstractmethod
    def dumps(cls, data: W) -> collections.abc.Iterable[collections.abc.Buffer]:
        """Get iterable with frame parts (usually header and payload)."""


class ConfigurableMessageFramingBase[R, W](abc.ABC):
    """Base abstract class for message framing implementations accepting parameters."""

    @abc.abstractmethod
    def frames(self, buffer: io.BytesIO) -> collections.abc.Iterable[int]:
        """Get iterator with required read sizes."""

    @abc.abstractmethod
    def loads(self, buffer: io.BytesIO) -> R:
        """Get frame payload from full buffer."""

    @abc.abstractmethod
    def dumps(self, data: W) -> collections.abc.Iterable[collections.abc.Buffer]:
        """Get iterable with frame parts (usually header and payload)."""


class VarIntBytes(MessageFramingBase):
    """VarInt-headered bytes message frames.

    This is the optimum possible framing for bytes, using SQLite4
    variable-length integers for the size header:
    - Header size is variable length from 1 to 9 bytes.
    - Maximum message length of 2**64 - 1.
    - 2 or 3 reads in total.

    """

    @classmethod
    def frames(cls, buffer: io.BytesIO) -> collections.abc.Generator[int, None, None]:
        """Iterate read size requests based on buffer contents."""
        yield 1
        yield _varint.peek(buffer.read()) - 1
        yield _varint.loads(buffer.getvalue())

    @classmethod
    def loads(cls, buffer: io.BytesIO) -> bytes:
        """Get frame payload from full buffer."""
        data = buffer.getbuffer()
        return data[_varint.peek(data):].tobytes()

    @classmethod
    def dumps[T: protocols.SizedBuffer](cls, data: T) -> tuple[bytes, T]:
        """Get tuple with header and payload."""
        return _varint.dumps(len(data)), data


try:
    import multiprocessing.connection as mp_conn
    import struct

    class MultiprocessingFramingBase(MessageFramingBase):
        """Base partially-abstract class for multiprocessing connection message frames.

        This framing implementation uses multiprocessing connection bytes messages:
        - Header of 4 or 12 bytes.
        - Maximum message length of 2**64 - 1.
        - 2 or 3 reads in total.

        """

        class _ReadableConnection(mp_conn.Connection):
            """Multiprocessing connection with buffered IO."""

            def __init__(self, buffer: io.BytesIO) -> None:
                """Initialize as readable with data."""
                super().__init__(0, readable=True)
                self.buffer = buffer.getbuffer()

            def _recv(self, size: int) -> io.BytesIO:
                """Read data from buffer."""
                data, self.buffer = self.buffer[:size], self.buffer[size:]
                return io.BytesIO(data)

            def _close(self) -> None:
                """Flag as closed."""
                self._handle = None

        class _WritableConnection(mp_conn.Connection):
            """Multiprocessing connection with buffered IO."""

            def __init__(self) -> None:
                """Initialize as writable."""
                super().__init__(0, writable=True)
                self.chunks = []

            def _send(self, buf: bytes) -> None:
                """Record data chunk."""
                self.chunks.append(buf)

            def _close(self) -> None:
                """Flag as closed."""
                self._handle = None

        @classmethod
        def frames(cls, buffer: io.BytesIO) -> collections.abc.Generator[int, None, None]:
            """Iterate read size requests based on buffer contents."""
            yield 4
            size, = struct.unpack('!i', buffer.read())
            if size == -1:
                yield 8
                size, = struct.unpack('!Q', buffer.read())
            yield size

    class MultiprocessingBytes(MultiprocessingFramingBase):
        """Multiprocessing connection bytes message frames."""

        @classmethod
        def loads(cls, buffer: io.BytesIO) -> bytes:
            """Get frame payload from full buffer."""
            return cls._ReadableConnection(buffer).recv_bytes()

        @classmethod
        def dumps(cls, data: collections.abc.Buffer) -> list[bytes]:
            """Get tuple with message data."""
            c = cls._WritableConnection()
            c.send_bytes(data)
            return c.chunks

    class Multiprocessing[T](MultiprocessingFramingBase):
        """Multiprocessing connection pickled message frames."""

        @classmethod
        def loads(cls, buffer: io.BytesIO) -> T:
            """Get unserialized frame payload from full buffer."""
            return cls._ReadableConnection(buffer).recv()

        @classmethod
        def dumps(cls, data: T) -> list[bytes]:
            """Get tuple with serialized message data."""
            c = cls._WritableConnection()
            c.send(data)
            return c.chunks

except ImportError:
    pass


try:
    import msgpack
    import msgpack.fallback

    PackerTypes = msgpack.Packer | msgpack.fallback.Packer
    UnpackerTypes = msgpack.Unpacker | msgpack.fallback.Unpacker

    class MsgPack[R, W](ConfigurableMessageFramingBase[R, W]):
        """Unheadered msgpack message."""

        packer: PackerTypes
        unpacker: UnpackerTypes

        _typedefs = (
            # headsize, headskip, varsized, recurse, factor
            *((0, 0, False, False, 1) for _ in range(0x80)),  # 0x00-0x80: fixint (+)
            *((i, 0, False, True, 2) for i in range(16)),  # 0x80-0x90: fixmap
            *((i, 0, False, True, 1) for i in range(16)),  # 0x90-0xA0: fixarr
            *((i, 0, False, False, 1) for i in range(32)),  # 0xA0-0xC0: fixstr
            (0, 0, False, False, 0),  # 0xC0: nil
            (),  # 0xC1: unused
            *((0, 0, False, False, 0) for i in range(2)),  # 0xC2-0xC3: false/true
            *((i, 0, True, False, 1) for i in (1, 2, 4)),  # 0xC4-0xC6: bin8/16/32
            *((i, 1, True, False, 1) for i in (1, 2, 4)),  # 0xC7-0xC9: ext8/16/32
            *((i, 0, False, False, 1) for i in (
                4, 8,  # 0xCA-0xCB: float32/64
                1, 2, 4, 8,  # 0xCC-0xCF: uint8/16/32/64
                1, 2, 4, 8,  # 0xD0-0xD3: int8/16/32/64
                )),
            *((i, 1, False, False, 1) for i in (1, 2, 4, 8, 16)),  # 0xD4-0xD9: fixext
            *((i, 0, True, False, 1) for i in (1, 2, 4)),  # 0xD9-0xDB: str8/16/32
            *((i, 0, True, True, 1) for i in (2, 4)),  # 0xDC-0xDD: arr16/32
            *((i, 0, True, True, 2) for i in (2, 4)),  # 0xDC-0xDD: map16/32
            *((0, 0, False, False, 1) for _ in range(0xE0, 0x100)),  # fixint (-)
            )

        def __init__(self, *, packer: PackerTypes | None = None, unpacker: UnpackerTypes | None = None) -> None:
            """Initialize."""
            super().__init__()
            self.packer = packer
            self.unpacker = unpacker

        def frames(self, buffer: io.BytesIO) -> collections.abc.Generator[int, None, None]:
            """Iterate read size requests based on buffer contents."""

            def fastforward() -> collections.abc.Generator[int, None, None]:
                """Iterate read size requests based on buffer contents."""
                fmt, = buffer.read(1)
                try:
                    size, extra, headered, recursion, factor = typedefs[fmt]

                except IndexError:
                    message = f'Unknown header: 0x{fmt:x}'
                    raise msgpack.FormatError(message) from None

                if headered:
                    yield size
                    size = int.from_bytes(buffer.read(size), 'big')

                if skip := size * factor + extra:
                    yield skip  # fastforward (or overcommit for recursion)

                if seek := (extra if recursion else skip):
                    buffer.seek(seek, seek_cur)

                if recursion and (items := size * factor):
                    for _ in range(items):
                        yield from fastforward()

            typedefs = self._typedefs
            seek_cur = os.SEEK_CUR
            yield 1
            yield from fastforward()

        def loads(self, buffer: io.BytesIO) -> R:
            """Get frame payload from full buffer."""
            unpacker = self.unpacker or msgpack.Unpacker()
            unpacker.feed(buffer.getbuffer())
            return unpacker.unpack()

        def dumps(self, data: W) -> tuple[bytes]:
            """Get tuple with header and payload."""
            if packer := self.packer:
                return packer.pack(data),
            return msgpack.packb(data),

except ImportError:
    pass
