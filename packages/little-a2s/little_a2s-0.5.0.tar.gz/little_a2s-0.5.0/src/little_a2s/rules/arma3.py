from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag
from typing import Mapping, Self

from little_a2s.events import ClientEventRules
from little_a2s.reader import Reader


@dataclass(kw_only=True)
class Arma3Rules:
    """A deserialized set of rules, mods, and signatures for Arma 3
    and similar Real Virtuality games like DayZ.

    Reference: https://community.bistudio.com/wiki/Arma_3:_ServerBrowserProtocol3

    .. versionadded:: 0.3.0

    """

    version: int
    """The version of this protocol."""
    overflow: int
    """General flags (overflow flags)."""
    dlc: Arma3DLC
    """A set of DLC flags indicated by the server.

    Some bits may be set that aren't part of this flag's members, up to 0xFFFF.

    """
    difficulty: Arma3Difficulty
    """The difficulty options defined by the server."""
    dlc_hashes: list[int]
    """A list of hashes for each DLC flag set, in order."""
    mods: list[Arma3Mod]
    """A list of mods that are required by the server, including CDLC."""
    signatures: list[str]
    """A list of key filenames loaded on the server, not including the .bikey suffix."""

    @classmethod
    def from_rules(cls, rules: Mapping[bytes, bytes] | ClientEventRules) -> Self:
        """Parse this class from a rules mapping.

        :raises EOFError: Not enough bytes could be read.
        :raises ValueError: The data is malformed.

        """
        if isinstance(rules, ClientEventRules):
            rules = rules.rules

        data = cls._assemble_rules(rules)
        data = cls._translate_escapes(data)
        reader = Reader(data)

        version = reader.read_byte()
        overflow = reader.read_byte()
        dlc = Arma3DLC(reader.read_ushort())
        difficulty = Arma3Difficulty.from_int(reader.read_ushort())
        dlc_hashes = [reader.read_ulong() for _ in range(dlc.bit_count())]

        n_mods = reader.read_byte()
        mods = [Arma3Mod.from_reader(reader) for _ in range(n_mods)]

        n_signatures = reader.read_byte()
        signatures = [reader.read_varchar1().decode() for _ in range(n_signatures)]

        return cls(
            version=version,
            overflow=overflow,
            dlc=dlc,
            difficulty=difficulty,
            dlc_hashes=dlc_hashes,
            mods=mods,
            signatures=signatures,
        )

    @staticmethod
    def _assemble_rules(rules: Mapping[bytes, bytes]) -> bytes:
        # Real Virtuality stores the payload in chunks of 125 bytes,
        # ordered and enumerated.
        data = bytearray()

        last_current = None
        last_total = None

        for k, v in rules.items():
            if len(k) != 2:
                continue

            current, total = k
            if last_total is not None and total != last_total:
                # This could be a legitimate two character key
                raise ValueError(f"Expected total {last_total}, got {total}")
            if last_current is not None and current != last_current + 1:
                raise ValueError(f"Expected index {last_current + 1}, got {current}")
            last_current, last_total = current, total

            data.extend(v)

            # We're making an assumption that the rules are encoded in order,
            # so last key should end with the same index.
            if current == total:
                break

        return bytes(data)

    @staticmethod
    def _translate_escapes(data: bytes) -> bytes:
        # FIXME: does this need to be optimized?
        data = data.replace(b"\x01\x03", b"\xff")
        data = data.replace(b"\x01\x02", b"\x00")
        data = data.replace(b"\x01\x01", b"\x01")
        return data


class Arma3DLC(IntFlag):
    """A set of DLC flags indicated by the server.

    Some bits may be set that aren't part of this flag's members, up to 0xFFFF.

    .. versionadded:: 0.3.0

    """

    KART = 0x1
    MARKSMEN = 0x2
    HELI = 0x4
    CURATOR = 0x8
    EXPANSION = 0x10
    JETS = 0x20
    ORANGE = 0x40  # Laws of War
    ARGO = 0x80
    TACOPS = 0x100
    TANKS = 0x200
    CONTACT = 0x400  # Contact platform
    ENOCH = 0x800  # Contact DLC
    ART_OF_WAR = 0x1000


@dataclass(kw_only=True)
class Arma3Difficulty:
    """The difficulty options defined by the server.

    .. versionadded:: 0.3.0

    """

    difficulty: int
    """The difficulty level, usually between 0-3."""
    skill: int
    """The AI skill level, usually between 0-3."""
    advanced_flight_model: bool
    """Indicates if Advanced Flight Model is enabled."""
    third_person_view: bool
    """Indicates if third-person view is enabled."""
    weapon_crosshair: bool
    """Indicates if the weapon crosshair is enabled."""

    @classmethod
    def from_int(cls, n: int) -> Self:
        """Parse this class from a 16-bit unsigned integer."""
        assert 0 <= n < 0xFFFF
        return cls(
            difficulty=n & 0b111,
            skill=n >> 3 & 0b111,
            advanced_flight_model=bool(n >> 6 & 0b1),
            third_person_view=bool(n >> 7 & 0b1),
            weapon_crosshair=bool(n >> 8 & 0b1),
        )


@dataclass(kw_only=True)
class Arma3Mod:
    """A mod required by the server.

    .. versionadded:: 0.3.0

    """

    hash: int
    """The 32-bit hash of that mod."""
    dlc: bool
    """Indicates if this is a DLC mod."""
    steam_id: int
    """The workshop ID of the mod, or app ID if it is DLC."""
    name: str
    """The name of the mod. Usually omitted for DLC."""

    @classmethod
    def from_reader(cls, reader: Reader) -> Self:
        """Parse this class from a reader.

        :raises EOFError: Not enough bytes could be read.
        :raises ValueError: The data is malformed.

        """
        hash = reader.read_ulong()

        length = reader.read_byte()
        dlc = bool(length >> 4 & 1)
        length = length & 0x0F
        steam_id = int.from_bytes(reader.read(length), "little")
        name = reader.read_varchar1().decode()

        return cls(
            hash=hash,
            dlc=dlc,
            steam_id=steam_id,
            name=name,
        )
