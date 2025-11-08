# socketwrapper

This package provides high level wrappers for sockets and pipes:

- Thread-safe within both threads and asyncio realms, and between them.
- Managed sync `recv` and `send` operations with timeouts.
- Native asyncio `recv_async` and `send_async` operations.
- Pluggable message protocol (headered variable length data) supporting variable-length header parsing, payload serialization and deserialization.
- Pluggable I/O protocol (OS file descriptor still required).

Builtin message protocols (framing):

- `socketwrapper.framing.VarIntBytes`: varint-headered bytes (default with `framing=True`).
- `socketwrapper.framing.MultiprocessingBytes` (if platform is supported): [multiprocessing.connection.Connection](https://docs.python.org/3.14/library/multiprocessing.html#connection-objects) bytes.
- `socketwrapper.framing.Multiprocessing` (if platform is supported): [multiprocessing.connection.Connection](https://docs.python.org/3.14/library/multiprocessing.html#connection-objects) pickled data.
- `socketwrapper.framing.MsgPack` (if `msgpack` is available): unheadered [msgpack](https://pypi.org/project/msgpack/) data stream.

## Motivation

- There aren't a ton of high level asyncio socket wrappers out there providing all we need for IPC: header/payload message logic and support for both sockets and pipes.
- Most implementations got either hardcoded messaging protocols or require a fixed-size header.
- No implementation was thread-safe between both asyncio and threading realms.
- No implementation directly supported wrapping multiprocessing Connections into an asyncio-native interface.

## Installation

```sh
uv pip install socketwrapper
```

Or with optional [msgpack](https://pypi.org/project/msgpack/) support.
```sh
uv pip install 'socketwrapper[msgpack]'
```

## Changelog

### 0.0.3 - 2025.11.08

- New: optional support for `recv_into` in socket-like objects.
- Optimization: recv operations will now use `sock.recv_into` (if available) to reduce memory allocation overhead.

### 0.0.2 - 2025.11.05

- Breaking: `MessageFraming.frames` and `MessageFraming.loads` now receive `io.BytesIO` instead of `bytearray`.
- New: optional msgpack support (`msgpack` extra).
- Fix: busy reads no longer blocking asyncio event loop.
- Typing: expose `SizedBuffer` and deprecate `SendPayload` (removal expected in `0.1.0`).
- Typing: `SocketWriter.send` and `SocketWriter.send_async` data is now `SizedBuffer`.

## Documentation

None other than this README, life's too short and I'm too busy with real life, if you need better documentation consider donating to [my ko-fi](https://ko-fi.com/s26me) stating that as a tip message, check out how my docs look like at [mstache docs](https://mstache.readthedocs.io/en/latest/) and [uactor docs](https://mstache.readthedocs.io/en/latest/).

### Puggable I/O: SocketLike protocol

The `protocols.SocketLike` protocol, a small subset the socket interface, is all what's required for any object to be wrap-able by `socketwrapper`.

Additional methods defined in `protocols.OptionalSocketLike` can be optionally implemented enabling optimized code paths.

```py
@typing.runtime_checkable
class SocketLike(typing.Protocol):
    """Protocol for socket-like objects accepted by socketwrapper socket classes."""

    def fileno(self) -> int: ...
    def send(self, data: collections.abc.Buffer, /) -> int: ...
    def recv(self, bufsize: int, /) -> bytes: ...
    def settimeout(self, timeout: float | None, /) -> None: ...
    def close(self) -> None: ...


@typing.runtime_checkable
class OptionalSocketLike(SocketLike, typing.Protocol):
    """Protocol for optional socket-like object methods accepted by socketwrapper socket classes."""

    def recv_into(self, buffer: collections.abc.Buffer, /) -> bytes: ...

```

Special attention to:
- [fileno](https://docs.python.org/3.14/library/socket.html#socket.socket.fileno) has to be a valid OS file descriptor.
- [settimeout](https://docs.python.org/3.14/library/socket.html#socket.socket.settimeout) must support `settimeout(.0)` ([non-blocking semantics](https://docs.python.org/3.14/library/socket.html#notes-on-socket-timeouts)), raising [ValueError](https://docs.python.org/3.14/library/exceptions.html#ValueError) for any other value will be handled, relying on [selectors.DefaultSelector](https://docs.python.org/3.14/library/selectors.html#selectors.DefaultSelector) for synchronous operations.

## Usage

### Simple IPC with pipe

```python
import os
import socketwrapper

with socketwrapper.pipe(framing=True) as (parent_reader, child_writer):
    child_writer.inheritable = True
    child_pid = os.fork()  # replace with your own process fork/spawn logic
    child_writer.inheritable = False  # important, prevent socket leaks!

    if child_pid:
        print(f'Message {parent_reader.recv()!r} received')
    else:
        child_writer.send(b'Hello world!')
```
```
Message b'Hello world!' received
```

### Simple IPC with pipe using msgpack

```python
import os
import socketwrapper
import socketwrapper.framing as framing

with socketwrapper.pipe(framing=framing.MsgPack()) as (parent_reader, child_writer):
    child_writer.inheritable = True
    child_pid = os.fork()  # replace with your own process fork/spawn logic
    child_writer.inheritable = False  # important, prevent socket leaks!

    if child_pid:
        print(f'Message {parent_reader.recv()!r} received')
    else:
        child_writer.send({'data': b'Hello world!'})
```
```
Message {'data': b'Hello world!'} received
```

### Simple asyncio IPC with pipe

```python
import asyncio
import os
import socketwrapper

async def parent(readable: socketwrapper.MessageReader) -> None:
    print(f'Message {await readable.recv_async()!r} received')

async def child(writable: socketwrapper.MessageWriter) -> None:
    await writable.send_async(b'Hello world!')

with socketwrapper.pipe(framing=True) as (parent_reader, child_writer):
    child_writer.inheritable = True
    child_pid = os.fork()  # replace with your own process fork/spawn logic
    child_writer.inheritable = False  # important, prevent socket leaks!

    asyncio.run(parent(parent_reader) if child_pid else child(child_writer))
```
```
Message b'Hello world!' received
```

### Simple bidirectional IPC with socketpair

```python
import os
import socketwrapper

with socketwrapper.socketpair(framing=True) as (parent_duplex, child_duplex):
    child_duplex.inheritable = True
    child_pid = os.fork()  # replace with your own process fork/spawn logic
    child_duplex.inheritable = False  # important, prevent socket leaks!

    if child_pid:
        parent_duplex.send(b'Hello child!')
        print(f'Message {parent_duplex.recv()!r} received in parent')

    else:
        print(f'Message {child_duplex.recv()!r} received in child')
        child_duplex.send(b'Hello parent!')
```
```
Message b'Hello child!' received in child
Message b'Hello parent!' received in parent
```

### Socketwrapper with multiprocessing.Pipe and asyncio

```py
import asyncio
import multiprocessing
import multiprocessing.connection
import socketwrapper
import socketwrapper.framing

def child(conn: multiprocessing.connection.Connection) -> None:

    async def main() -> None:
        with socketwrapper.MessageDuplex(conn, framing=socketwrapper.framing.MultiprocessingBytes) as child_duplex:
            print(f'Message {await child_duplex.recv_async()!r} received in child')
            await child_duplex.send_async(b'Hello parent!')

    asyncio.run(main())

if __name__ == '__main__':
    parent_conn, child_conn = multiprocessing.Pipe()
    with parent_conn, child_conn:
        child_process = multiprocessing.Process(target=child, args=(child_conn,))
        child_process.start()

        parent_conn.send_bytes(b'Hello child!')
        print(f'Message {parent_conn.recv_bytes()!r} received in parent')
        child_process.join(1)
```
```
Message b'Hello child!' received in child
Message b'Hello parent!' received in parent
```

### Socketwrapper for cross-interpreter communication

```py
import concurrent.futures
import socketwrapper

def child(child_fileno: int) -> None:
    child_writer = socketwrapper.MessageWriter(child_fileno)
    child_writer.send(b'Hello World')

if __name__ == '__main__':
    with (socketwrapper.pipe(framing=True) as (parent_reader, child_writer),
          concurrent.futures.InterpreterPoolExecutor() as pool):
        pool.submit(child, child_writer.fileno())
        print(f'Message {parent_reader.recv()!r} received')
```
```
Message b'Hello World' received
```

### Custom socketwrapper framing with progress

```py
import collections.abc
import io
import itertools
import os
import socketwrapper
import socketwrapper.framing

def progress(arrow: str, size: int, min_chunk: int = 1024) -> collections.abc.Generator[int, None, None]:
    part_size = max(min_chunk, size // 100)
    full_parts, last_size = divmod(size, part_size)
    percent = 100 / (full_parts + 1 if last_size else full_parts)

    for i in range(full_parts):
        print(f'{arrow} {i * percent:6.2f}%')
        yield part_size

    if last_size:
        print(f'{arrow} {full_parts * percent:6.2f}%')
        yield last_size

    print(f'{arrow} 100%')

class ProgressFraming(socketwrapper.framing.VarIntBytes):

    @classmethod
    def frames(cls, buffer: io.BytesIO) -> collections.abc.Generator[int, None, None]:
        frames = super().frames(buffer)
        yield from itertools.islice(frames, 2)
        yield from progress('>', next(frames))

    @classmethod
    def dumps(cls, data: bytes) -> collections.abc.Generator[memoryview, None, None]:
        buffer = memoryview(b''.join(super().dumps(data)))
        for size in progress('<', len(buffer)):
            chunk, buffer = buffer[:size], buffer[size:]
            yield chunk

with socketwrapper.socketpair(framing=ProgressFraming) as (parent_duplex, child_duplex):
    child_duplex.inheritable = True
    child_pid = os.fork()  # replace with your own multiprocessing fork logic
    child_duplex.inheritable = False  # important, prevent socket leaks!

    if child_pid:
        payload = os.urandom(1024) * 1024
        print(f'Sending {len(payload)} bytes!')
        parent_duplex.send(payload)
    else:
        print(f'Received {len(child_duplex.recv())} bytes!')
```
```
Sending 1048576 bytes!
<   0.00%
<   0.99%
<   1.98%
<   2.97%
...
>   0.99%
<  13.86%
>   1.98%
<  14.85%
...
>  91.09%
<  99.01%
>  92.08%
< 100%
...
>  98.02%
>  99.01%
> 100%
Received 1048576 bytes!
```
