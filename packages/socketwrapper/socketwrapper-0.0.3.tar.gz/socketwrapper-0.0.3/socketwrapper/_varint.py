r"""SQLite4 varint tools.

Implementation of SQLite4 Variable-Length Integers
==================================================

Based on spec at https://sqlite.org/src4/doc/trunk/www/varint.wiki

Examples
--------
>>> tests = {
...     b'\x00': 0,
...     b'\xf0': 240,
...     b'\xf8\xff': 2287,
...     b'\xf9\xff\xff': 67823,
...     b'\xfa\xff\xff\xff': 2**24 - 1,
...     b'\xfb\xff\xff\xff\xff': 2**32 - 1,
...     b'\xfc\xff\xff\xff\xff\xff': 2**40 - 1,
...     b'\xfd\xff\xff\xff\xff\xff\xff': 2**48 - 1,
...     b'\xfe\xff\xff\xff\xff\xff\xff\xff': 2**56 - 1,
...     b'\xff\xff\xff\xff\xff\xff\xff\xff\xff': 2**64 - 1,
...     }

>>> [peek(i[:1]) for i in tests] == [len(i) for i in tests]
True

>>> [dumps(i) for i in tests.values()] == list(tests)
True

>>> [loads(i) for i in tests] == list(tests.values())
True

>>> dumps(2**64)
Traceback (most recent call last):
...
OverflowError: int too big to convert

"""

import collections.abc
import typing


class VarIntBytes(typing.Protocol):
    @typing.overload
    def __getitem__(self, key: typing.SupportsIndex, /) -> int: ...

    @typing.overload
    def __getitem__(self, key: slice, /) -> (
        collections.abc.Iterable[typing.SupportsIndex]
        | typing.SupportsBytes
        | collections.abc.Buffer
        ): ...


def peek(data: VarIntBytes | int) -> int:
    """Get total varint bytesize from its first byte."""
    start = data if isinstance(data, int) else data[0]
    return (
        1 if start < 0xF1 else
        2 if start < 0xF9 else
        3 if start < 0xFA else
        start - 0xF6
        )


def dumps(value: int) -> bytes:
    """Encode given unsigned integer as varint bytes."""
    return (
        value.to_bytes() if value < 0xF1 else
        (0xF010 + value).to_bytes(2) if value < 0x8F0 else
        (0xF8F710 + value).to_bytes(3) if value < 0x108F0 else
        (0xFA000000 | value).to_bytes(4) if value < 0x1000000 else
        (0xFB00000000 | value).to_bytes(5) if value < 0x100000000 else
        (0xFC0000000000 | value).to_bytes(6) if value < 0x10000000000 else
        (0xFD000000000000 | value).to_bytes(7) if value < 0x1000000000000 else
        (0xFE00000000000000 | value).to_bytes(8) if value < 0x100000000000000 else
        (0xFF0000000000000000 + value).to_bytes(9)
        )


def loads(data: VarIntBytes) -> int:
    """Decode given varint bytes as integer."""
    start = data[0]
    return (
        start if start < 0xF1 else
        int.from_bytes(data[:2]) - 0xF010 if start < 0xF9 else
        int.from_bytes(data[:3]) - 0xF8F710 if start < 0xFA else
        int.from_bytes(data[1:start - 0xF6])
        )


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True, raise_on_error=True, exclude_empty=True, optionflags=doctest.ELLIPSIS)
