# https://developer.valvesoftware.com/wiki/Server_queries
from dataclasses import dataclass
from enum import IntEnum

from little_a2s.enums import _EnumReprMixin


class HeaderType(_EnumReprMixin, IntEnum):
    SIMPLE = -1
    """Means the response isn't split."""
    MULTI = -2
    """Means the response is split."""


@dataclass(kw_only=True)
class Compression:
    """The compression header for Source games. Mostly present in ~2006-era engines."""

    size: int
    """Size of the whole response once it is decompressed."""
    checksum: int
    """CRC32 checksum of uncompressed response."""


@dataclass(kw_only=True)
class Header:
    """An A2S response header."""


@dataclass(kw_only=True)
class SimpleHeader(Header):
    """An single-packet A2S response header."""


@dataclass(kw_only=True)
class MultiHeader(Header):
    """A multi-packet A2S response header for Source games."""

    id: int
    """Unique number assigned by server per answer."""
    current: int
    """The number of the packet."""
    total: int
    """The total number of packets in the response."""
    size: int  # Some games omit this field!
    """The maximum size of packet before packet switching occurs, usually 1248 bytes."""
    compressed: Compression | None
    """An optional compression header. Mostly present in ~2006-era engines."""


@dataclass(kw_only=True)
class MultiGoldsourceHeader(Header):
    """A multi-packet A2S response header for Goldsource games."""

    id: int
    """Unique number assigned by server per answer."""
    current: int
    """The number of the packet."""
    total: int
    """The total number of packets in the response."""
