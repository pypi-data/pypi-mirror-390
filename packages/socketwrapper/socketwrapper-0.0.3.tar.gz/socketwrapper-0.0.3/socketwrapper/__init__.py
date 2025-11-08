"""socketwrapper - Message socket wrappers."""

import asyncio
import collections.abc
import io
import os
import selectors
import socket
import stat
import sys
import typing


if sys.version_info < (3, 13):
    import typing_extensions
else:
    typing_extensions = typing


from . import _utils, framing, protocols


__all__ = (
    # type aliases and protocols
    'MessageFraming',
    'SendPayload',  # TODO(0.1.0): remove, deprecated since 0.0.2
    'SizedBuffer',
    'SocketLike',
    'SocketOrDescriptor',

    # wrappers
    'SocketWrapper',
    'SocketReader',
    'SocketWriter',
    'SocketDuplex',

    'MessageWrapper',
    'MessageReader',
    'MessageWriter',
    'MessageDuplex',

    # utils
    'pipe',
    'socketpair',
    )


DEFAULT_SOCKETPAIR_FAMILY = getattr(socket, 'AF_UNIX', socket.AF_INET)
DEFAULT_FRAMING = framing.VarIntBytes

SocketLike = protocols.SocketLike
MessageFraming = protocols.MessageFraming
SocketOrDescriptor = protocols.SocketLike | protocols.ExtendedSocketLike | protocols.HasFileno | int
SizedBuffer = protocols.SizedBuffer

RecvSize = _utils.RecvSize
SendPayload = _utils.SendPayload


class DescriptorSocket:
    """Generic socket-like accepting any file descriptor (usually pipes) as input."""

    def __init__(self, fd: int) -> None:
        """Initialize."""
        self._fd = fd

    def fileno(self) -> int:
        """Get underlying file descriptor."""
        return self._fd

    def send(self, data: collections.abc.Buffer) -> int:
        """Write data to descriptor."""
        return os.write(self._fd, data)

    def recv(self, bufsize: int) -> bytes:
        """Read data from descriptor."""
        return os.read(self._fd, bufsize)

    if sys.version_info < (3, 14):
        def recv_into(self, buffer: collections.abc.Buffer) -> int:
            """Read data from descriptor into buffer."""
            return os.readv(self._fd, (buffer,))

    else:
        def recv_into(self, buffer: collections.abc.Buffer) -> int:
            """Read data from descriptor into buffer."""
            return os.readinto(self._fd, buffer)

    def settimeout(self, timeout: float | None) -> None:
        """Set blocking or non-blocking based on timeout being 0 or None."""
        if timeout:
            raise ValueError(timeout)

        os.set_blocking(self._fd, timeout is None)

    def close(self) -> None:
        """Close file descriptor."""
        os.close(self._fd)


class SocketWrapper(_utils.ClosingContext):
    """Base class for socket wrappers supporting asynchronous operations."""

    _sock: SocketLike
    _duplex: bool = False
    _wselector: selectors.BaseSelector | None = None
    _rselector: selectors.BaseSelector | None = None

    def __init__(self, sock: SocketOrDescriptor) -> None:
        """Initialize for socket."""
        self._sock = _socketlike(sock)

    @property
    def inheritable(self) -> bool:
        """Get whether or not this socket is inheritable by subprocesses."""
        return os.get_inheritable(self._sock.fileno())

    @inheritable.setter
    def inheritable(self, inheritable: bool) -> None:
        """Set whether or not this socket is inheritable by subprocesses."""
        os.set_inheritable(self._sock.fileno(), inheritable)

    def fileno(self) -> int:
        """Get underlying socket file descriptor."""
        return self._sock.fileno()

    def close(self) -> None:
        """Close underlying socket."""
        for obj in (self._rselector, self._wselector, self._sock):
            if obj:
                obj.close()

    def _selector(self, *, write: bool = False) -> collections.abc.Callable[[float | None], list[tuple]]:
        """Get selector for socket."""
        sel = self._wselector if write else self._rselector
        if not sel:
            sel = selectors.DefaultSelector()
            if write:
                sel.register(self._sock.fileno(), selectors.EVENT_WRITE)
                self._wselector = sel

            else:
                sel.register(self._sock.fileno(), selectors.EVENT_READ)
                self._rselector = sel

        return sel.select

    def _consume(self, processor: collections.abc.Iterable, deadline: float | None, *, write: bool = False) -> None:
        """Configure socket and consume processor."""
        timeout = _utils.timeout_checker(deadline, 'timeout during transmission') if deadline else None
        wait = self._sock.settimeout if timeout else None
        if self._duplex or not _utils.safe_timeout(self._sock, timeout() if timeout else None):
            self._sock.settimeout(.0)
            wait = self._selector(write=write)

        if wait and timeout:
            for _ in processor:
                wait(timeout())

        elif wait:
            for _ in processor:
                wait(None)

        else:
            for _ in processor:
                pass

    async def _consume_async(self, processor: collections.abc.Iterable, *, write: bool = False) -> None:
        """Configure socket as non-blocking and consume processor."""
        loop = asyncio.get_event_loop()
        add_io, remove_io = (
            (loop.add_writer, loop.remove_writer) if write else
            (loop.add_reader, loop.remove_reader)
            )

        self._sock.settimeout(.0)
        event = asyncio.Event()
        add_io(self, event.set)
        try:
            for empty in processor:
                if empty:
                    event.clear()
                    await event.wait()

                else:
                    await asyncio.sleep(0)

        finally:
            remove_io(self)


class SocketReader(SocketWrapper):
    """Readable socket wrapper."""

    _rlock: _utils.CrossLock

    def __init__(self, sock: SocketOrDescriptor) -> None:
        """Initialize for socket."""
        super().__init__(sock)
        self._rlock = _utils.CrossLock()

    def _recv(self, bufsize: RecvSize, timeout: float | None = None) -> io.BytesIO:
        """Receive data from socket as bytearray."""
        with _utils.lock_timeout(self._rlock, timeout=timeout) as deadline:
            buffer = io.BytesIO()
            reader = _utils.reader(self._sock, buffer, bufsize)
            self._consume(reader, deadline)
            return buffer

    async def _recv_async(self, bufsize: RecvSize) -> io.BytesIO:
        """Receive data from socket (async) as bytearray."""
        async with self._rlock:
            buffer = io.BytesIO()
            reader = _utils.reader(self._sock, buffer, bufsize, throttle=True)
            await self._consume_async(reader)
            return buffer

    def recv(self, bufsize: int, timeout: float | None = None) -> bytes:
        """Receive data from socket as bytes."""
        return self._recv(bufsize, timeout).getvalue()

    async def recv_async(self, bufsize: int) -> bytes:
        """Receive data from socket (async) as bytes."""
        return (await self._recv_async(bufsize)).getvalue()


class SocketWriter(SocketWrapper):
    """Writable socket wrapper."""

    _wlock: _utils.CrossLock

    def __init__(self, sock: SocketOrDescriptor) -> None:
        """Initialize for socket."""
        super().__init__(sock)
        self._wlock = _utils.CrossLock()

    def _send(self, data: SendPayload, timeout: float | None = None) -> None:
        """Send data to socket."""
        with _utils.lock_timeout(self._wlock, timeout=timeout) as deadline:
            writer = _utils.writer(self._sock, data)
            self._consume(writer, deadline, write=True)

    async def _send_async(self, data: SendPayload) -> None:
        """Send data to socket (async)."""
        async with self._wlock:
            writer = _utils.writer(self._sock, data, throttle=True)
            await self._consume_async(writer, write=True)

    def send(self, data: SizedBuffer, timeout: float | None = None) -> None:
        """Send data to socket."""
        self._send(data, timeout=timeout)

    async def send_async(self, data: SizedBuffer) -> None:
        """Send data to socket (async)."""
        await self._send_async(data)


class SocketDuplex(SocketWriter, SocketReader):
    """Duplex (both readable and writable) socket wrapper."""

    _duplex: bool = True


# TODO(py313+): use new syntax
R = typing.TypeVar('R')
W = typing.TypeVar('W')
KS = typing_extensions.TypeVar('KS', bound=SocketWrapper, default=SocketWrapper)
KSR = typing_extensions.TypeVar('KSR', bound=SocketReader, default=SocketReader)
KSW = typing_extensions.TypeVar('KSW', bound=SocketWriter, default=SocketWriter)


class MessageWrapper(_utils.ClosingContext, typing_extensions.Generic[R, W, KS]):
    """Base class for message socket wrappers supporting asynchronous operations."""

    _wrapper = SocketWrapper
    _raw: KS
    framing: MessageFraming[R, W]

    def __init__(self, sock: KS | SocketOrDescriptor, framing: MessageFraming[R, W] = DEFAULT_FRAMING) -> None:
        """Initialize for socket."""
        self._raw = sock if isinstance(sock, SocketWrapper) else self._wrapper(sock)
        self.framing = framing

    @property
    def inheritable(self) -> bool:
        """Get whether or not this socket is inheritable by subprocesses."""
        return self._raw.inheritable

    @inheritable.setter
    def inheritable(self, inheritable: bool) -> None:
        """Set whether or not this socket is inheritable by subprocesses."""
        self._raw.inheritable = inheritable

    def fileno(self) -> int:
        """Get underlying socket file descriptor."""
        return self._raw.fileno()

    def close(self) -> None:
        """Close underlying socket."""
        self._raw.close()


class MessageReader(MessageWrapper[R, typing.Any, KSR], typing_extensions.Generic[R, KSR]):
    """Readable message socket wrapper."""

    _wrapper = SocketReader

    def recv(self, timeout: float | None = None) -> R:
        """Receive data from socket."""
        return self.framing.loads(self._raw._recv(self.framing.frames, timeout=timeout))

    async def recv_async(self) -> R:
        """Receive data from socket (async)."""
        return self.framing.loads(await self._raw._recv_async(self.framing.frames))


class MessageWriter(MessageWrapper[typing.Any, W, KSW], typing_extensions.Generic[W, KSW]):
    """Writable message socket wrapper."""

    _wrapper = SocketWriter

    def send(self, data: W, timeout: float | None = None) -> None:
        """Send data to socket."""
        self._raw._send(self.framing.dumps(data), timeout=timeout)

    async def send_async(self, data: W) -> None:
        """Send data to socket (async)."""
        await self._raw._send_async(self.framing.dumps(data))


class MessageDuplex[R, W](MessageWriter[W, SocketDuplex], MessageReader[R, SocketDuplex]):
    """Duplex (both readable and writable) message socket wrapper."""

    _wrapper = SocketDuplex


# TODO: move to namespace
_WrapperPair = _utils.ContextPair[SocketReader, SocketWriter]
_DuplexWrapperPair = _utils.ContextPair[SocketDuplex, SocketDuplex]
_DefaultMessagePair = _utils.ContextPair[MessageReader[bytes], MessageWriter[protocols.SizedBuffer]]
_DuplexDefaultMessagePair = _utils.ContextPair[
    MessageDuplex[bytes, protocols.SizedBuffer],
    MessageDuplex[bytes, protocols.SizedBuffer],
    ]


@typing.overload
def socketpair(
    family: int = ...,
    type: typing.Literal[socket.SocketKind.SOCK_STREAM] = socket.SOCK_STREAM,
    proto: int = ...,
    framing: typing.Literal[False] = False,
    ) -> _DuplexWrapperPair: ...


@typing.overload
def socketpair(
    family: int = ...,
    type: socket.SocketKind | int = socket.SOCK_STREAM,
    proto: int = ...,
    framing: typing.Literal[False] = False,
    ) -> _WrapperPair: ...


@typing.overload
def socketpair(
    family: int = ...,
    type: typing.Literal[socket.SocketKind.SOCK_STREAM] = socket.SOCK_STREAM,
    proto: int = ...,
    framing: typing.Literal[True] = ...,
    ) -> _DefaultMessagePair: ...


@typing.overload
def socketpair(
    family: int = ...,
    type: socket.SocketKind | int = ...,
    proto: int = ...,
    framing: typing.Literal[True] = ...,
    ) -> _DuplexDefaultMessagePair: ...


@typing.overload
def socketpair[R, W](
    family: int = ...,
    type: typing.Literal[socket.SocketKind.SOCK_STREAM] = socket.SOCK_STREAM,
    proto: int = ...,
    framing: MessageFraming[R, W] = ...,
    ) -> _utils.ContextPair[MessageDuplex[R, W], MessageDuplex[R, W]]: ...


@typing.overload
def socketpair[R, W](
    family: int = ...,
    type: socket.SocketKind | int = ...,
    proto: int = ...,
    framing: MessageFraming[R, W] = ...,
    ) -> _utils.ContextPair[MessageReader[R], MessageWriter[W]]: ...


def socketpair(
        family=DEFAULT_SOCKETPAIR_FAMILY,
        type=socket.SOCK_STREAM,  # noqa: A002
        proto=0,
        framing=False,
        ):
    """Initialize connected socket pair as socket wrappers, or message wrappers if framing is enabled."""
    sock_a, sock_b = socket.socketpair(family, type, proto)
    return (
        _utils.ContextPair(_duplex(sock_a, framing), _duplex(sock_b, framing)) if type == socket.SOCK_STREAM else
        _utils.ContextPair(_reader(sock_a, framing), _writer(sock_b, framing))
        )


@typing.overload
def pipe(framing: typing.Literal[False] = False) -> _WrapperPair: ...


@typing.overload
def pipe(framing: typing.Literal[True]) -> _DefaultMessagePair: ...


@typing.overload
def pipe[R, W](framing: MessageFraming[R, W]) -> _utils.ContextPair[MessageReader[R], MessageWriter[W]]: ...


def pipe(framing=False):
    """Initialize pipe (readable, writable) as socket wrapper pair, or message wrappers pair if framing is enabled."""
    read_fd, write_fd = os.pipe()
    return _utils.ContextPair(_reader(read_fd, framing), _writer(write_fd, framing))


def _reader[R, W](sock: SocketOrDescriptor, framing: MessageFraming[R, W] | bool) -> SocketReader | MessageReader[R]:
    """Initialize bytes or message reader wrapper based on framing."""
    return MessageReader(sock, fr) if (fr := _framing(framing)) else SocketReader(sock)


def _writer[R, W](sock: SocketOrDescriptor, framing: MessageFraming[R, W] | bool) -> SocketWriter | MessageWriter[W]:
    """Initialize bytes or message writer wrapper based on framing."""
    return MessageWriter(sock, fr) if (fr := _framing(framing)) else SocketWriter(sock)


def _duplex[R, W](sock: SocketOrDescriptor, framing: MessageFraming[R, W] | bool) -> SocketDuplex | MessageDuplex[R, W]:
    """Initialize duplex bytes or message wrapper based on framing."""
    return MessageDuplex(sock, fr) if (fr := _framing(framing)) else SocketDuplex(sock)


# TODO(py313+): use new syntax
DR = typing_extensions.TypeVar('DR', default=bytes)
DW = typing_extensions.TypeVar('DW', default=protocols.SizedBuffer)


def _framing(framing: MessageFraming[DR, DW] | bool) -> MessageFraming[DR, DW] | None:
    """Pick framing (or default framing) based on framing parameter."""
    return DEFAULT_FRAMING if framing is True else framing if framing else None


def _socketlike[S: SocketLike](sock: S | protocols.HasFileno | int) -> S | socket.socket | DescriptorSocket:
    """Use or initialize socketlike, reporting if it's native or not."""
    if isinstance(sock, protocols.SocketLike):
        return sock  # socket object, use straight

    fd, dup = (sock, False) if isinstance(sock, int) else (sock.fileno(), True)

    try:
        maybe_socket = os.name == 'nt' or stat.S_ISSOCK(os.fstat(fd).st_mode)

    except Exception:
        maybe_socket = False

    if maybe_socket:
        sck = socket.socket(fileno=fd)
        try:
            sck.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
            if dup:  # obj backed by socket, duplicate to not interfere with original ref lifetime
                sck2 = sck.dup()
                sck.detach()
                return sck2

        except OSError:
            sck.detach()

        else:
            return sck  # socket descriptor, use directly

    return DescriptorSocket(fd)  # assume pipe-like
