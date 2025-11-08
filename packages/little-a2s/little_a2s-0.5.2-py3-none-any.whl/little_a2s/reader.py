import struct
from io import BytesIO
from typing import Literal, Protocol, runtime_checkable


@runtime_checkable
class Readable(Protocol):
    def read(self, n: int = -1, /) -> bytes:
        """Read up to n bytes, or the entire stream if n is negative."""
        raise NotImplementedError


class Reader:
    """A simple reader for parsing serialized data."""

    def __init__(self, data: bytes | Readable) -> None:
        if not isinstance(data, Readable):
            data = BytesIO(data)

        self._file = data

    def read(self, n: int = -1, /) -> bytes:
        """Read exactly n bytes, or the entire stream if n is negative.

        :raises EOFError: Not enough bytes could be read.

        """
        data = self._file.read(n)
        if n >= 0 and len(data) < n:
            raise EOFError
        return data

    def read_byte(self) -> int:
        """Read a single unsigned byte.

        :raises EOFError: Not enough bytes could be read.

        """
        return self.read(1)[0]

    def read_char(self) -> str:
        """Read a single ASCII character.

        :raises EOFError: Not enough bytes could be read.

        """
        return self.read(1).decode("ascii")

    def read_null(self) -> Literal[0]:
        """Read a null byte.

        :raises EOFError: Not enough bytes could be read.
        :raises ValueError: A non-null byte was read.

        """
        n = self.read_byte()
        if n != 0:
            raise ValueError(f"Expected null byte, got {n!r}")
        return n

    def read_short(self) -> int:
        """Read a signed 16-bit integer.

        :raises EOFError: Not enough bytes could be read.

        """
        return int.from_bytes(self.read(2), "little", signed=True)

    def read_ushort(self) -> int:
        """Read an unsigned 16-bit integer.

        :raises EOFError: Not enough bytes could be read.

        """
        return int.from_bytes(self.read(2), "little")

    def read_long(self) -> int:
        """Read a signed 32-bit integer.

        :raises EOFError: Not enough bytes could be read.

        """
        return int.from_bytes(self.read(4), "little", signed=True)

    def read_ulong(self) -> int:
        """Read an unsigned 32-bit integer.

        :raises EOFError: Not enough bytes could be read.

        """
        return int.from_bytes(self.read(4), "little")

    def read_float(self) -> float:
        """Read a 32-bit float.

        :raises EOFError: Not enough bytes could be read.

        """
        return struct.unpack("<f", self.read(4))[0]

    def read_uint64(self) -> int:
        """Read an unsigned 64-bit integer.

        :raises EOFError: Not enough bytes could be read.

        """
        return int.from_bytes(self.read(8), "little")

    def read_null_string(self) -> bytes:
        """Read a null-terminated byte string.

        :raises EOFError: Not enough bytes could be read.

        """
        return self.read_until(0)

    def read_null_utf8(self) -> str:
        """Read a null-terminated, UTF-8 decoded string.

        :raises EOFError: Not enough bytes could be read.
        :raises UnicodeDecodeError: The string could not be decoded as UTF-8.

        """
        s = self.read_null_string()
        return s.decode()

    def read_until(self, sep: int) -> bytes:
        """Read until the sep character is found and return all bytes before sep.

        :raises EOFError: Not enough bytes could be read.

        """
        if not 0x00 <= sep < 0xFF:
            raise ValueError(f"Expected sep in range [0, 255], got {sep!r}")

        # FIXME: is this hot loop slow?
        data = bytearray()
        while (char := self.read_byte()) != sep:
            data.append(char)

        return bytes(data)

    def read_varchar1(self) -> bytes:
        """Read a byte ``length`` and then return exactly ``length`` bytes.

        :raises EOFError: Not enough bytes could be read.

        """
        length = self.read_byte()
        return self.read(length)

    def read_varchar2(self) -> bytes:
        """Read a 2-byte ``length`` and then return exactly ``length`` bytes.

        :raises EOFError: Not enough bytes could be read.

        """
        length = self.read_ushort()
        return self.read(length)

    def read_varchar4(self) -> bytes:
        """Read a 4-byte ``length`` and then return exactly ``length`` bytes.

        :raises EOFError: Not enough bytes could be read.

        """
        length = self.read_ulong()
        return self.read(length)

    def read_varchar8(self) -> bytes:
        """Read an 8-byte ``length`` and then return exactly ``length`` bytes.

        :raises EOFError: Not enough bytes could be read.

        """
        length = self.read_uint64()
        return self.read(length)
