from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Packet:
    """The base class of all A2S packets."""


@dataclass(kw_only=True)
class ClientPacket(Packet):
    """An A2S packet sent by the client.

    This class and its subclasses can be coerced into byte streams by passing
    to :class:`bytes() <bytes>`, for example ``bytes(packet)``.

    """

    header: bytes
    """The header of the request."""
    payload: bytes
    """The payload of the request."""
    challenge: int
    """The challenge number last given by the server."""

    def __bytes__(self) -> bytes:
        challenge = self.challenge.to_bytes(4, "little", signed=True)
        return b"".join((self.header, self.payload, challenge))


@dataclass(kw_only=True)
class ClientPacketInfo(ClientPacket):
    """An A2S_INFO packet sent by the client."""

    header: bytes = field(default=b"\xff\xff\xff\xff\x54", init=False)
    payload: bytes = field(default=b"Source Engine Query\x00", init=False)
    challenge: int = -1


@dataclass(kw_only=True)
class ClientPacketPlayers(ClientPacket):
    """An A2S_PLAYER packet sent by the client."""

    header: bytes = field(default=b"\xff\xff\xff\xff\x55", init=False)
    payload: bytes = field(default=b"", init=False)
    challenge: int = -1


@dataclass(kw_only=True)
class ClientPacketRules(ClientPacket):
    """An A2S_RULES packet sent by the client."""

    header: bytes = field(default=b"\xff\xff\xff\xff\x56", init=False)
    payload: bytes = field(default=b"", init=False)
    challenge: int = -1
