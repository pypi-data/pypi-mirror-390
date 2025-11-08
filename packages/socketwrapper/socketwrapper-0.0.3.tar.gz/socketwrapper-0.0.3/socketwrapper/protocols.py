"""Standard python protocols used by socketwrapper."""

import collections.abc
import io
import typing


@typing.runtime_checkable
class SizedBuffer(typing.Protocol):
    """Protocol for buffers with size."""

    def __buffer__(self, flags: int, /) -> memoryview: ...
    def __len__(self) -> int: ...


@typing.runtime_checkable
class SocketLike(typing.Protocol):
    """Protocol for socket-like objects accepted by socketwrapper socket classes."""

    def fileno(self) -> int: ...
    def send(self, data: collections.abc.Buffer, /) -> int: ...
    def recv(self, bufsize: int, /) -> bytes: ...
    def settimeout(self, timeout: float | None, /) -> None: ...
    def close(self) -> None: ...


@typing.runtime_checkable
class ExtendedSocketLike(SocketLike, typing.Protocol):
    """Protocol for optional socket-like object methods accepted by socketwrapper socket classes."""

    def recv_into(self, buffer: collections.abc.Buffer, /) -> bytes: ...


@typing.runtime_checkable
class HasFileno(typing.Protocol):
    """Protocol for objects backed by a file descriptor."""

    def fileno(self) -> int: ...


@typing.runtime_checkable
class MessageFraming[R, W](typing.Protocol):
    """Protocol for message framing implementations accepted by socketwrapper message classes."""

    def frames(self, buffer: io.BytesIO, /) -> collections.abc.Iterable[int]: ...
    def loads(self, buffer: io.BytesIO, /) -> R: ...
    def dumps(self, data: W, /) -> collections.abc.Iterable[SizedBuffer]: ...
