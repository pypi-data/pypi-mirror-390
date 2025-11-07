# import asyncio
import socket
from contextlib import suppress
from typing import Callable, Iterable, Iterator, Self, Type, TypeVar

from little_a2s.events import (
    ClientEvent,
    ClientEventChallenge,
    ClientEventGoldsourceInfo,
    ClientEventInfo,
    ClientEventPlayers,
    ClientEventRules,
)
from little_a2s.packets import ClientPacket
from little_a2s.protocol import A2SClientProtocol, A2SGoldsourceClientProtocol

DEFAULT_TIMEOUT = 3.0

T = TypeVar("T")
ClientEventT = TypeVar("ClientEventT", bound=ClientEvent)


def filter_type(
    t: Type[T] | tuple[Type[T], ...],
    it: Iterable[object],
    /,
) -> Iterator[T]:
    """Filter through an iterable for elements of the given type."""
    for x in it:
        if isinstance(x, t):
            yield x


def first(t: Type[T] | tuple[Type[T], ...], it: Iterable[object], /) -> T | None:
    """Return the first element of the given type in an iterable."""
    return next(filter_type(t, it), None)


def last(t: Type[T] | tuple[Type[T], ...], it: Iterable[object], /) -> T | None:
    """Return the last element of the given type in an iterable."""
    x = None
    for x in filter_type(t, it):
        pass
    return x


class A2S:
    """A synchronous client for A2S queries.

    ::

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.connect(("127.0.0.1", 27015))
        with A2S(sock) as a2s:
            print(a2s.info())
            print(a2s.players())
            print(a2s.rules())

    This follows the Source format. For the Goldsource equivalent,
    see :class:`A2SGoldsource`.

    This class supports the context manager protocol which automatically
    closes the socket upon exit.

    :param sock:
        The UDP socket to send and receive queries from.
        The socket **must** be connected to a remote address beforehand
        with :meth:`~socket.socket.connect()`. You may also want to
        set a timeout with :meth:`~socket.socket.settimeout()`.
        Alternatively, use :meth:`from_addr()` to construct the socket for you.
    :param challenge:
        The initial challenge sequence to use for requests.
        This is optional if you close the socket and want to resume
        sending queries shortly afterwards without an extra challenge
        response. However, the server may still challenge you regardless.

    """

    buffer_size = 32768  # probably overkill?
    _events: list[ClientEvent]

    def __init__(self, sock: socket.socket, *, challenge: int = -1) -> None:
        if sock.type != socket.SOCK_DGRAM:
            raise ValueError("Socket type must be SOCK_DGRAM")

        self._sock = sock
        self._protocol = self._create_protocol(challenge=challenge)
        self._events = []

    def __enter__(self) -> Self:
        self._sock.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, tb) -> None:
        return self._sock.__exit__(exc_type, exc_val, tb)

    def events_received(self) -> list[ClientEvent]:
        """Purge all outstanding events not returned by other methods."""
        events, self._events = self._events, []
        return events

    def info(self) -> ClientEventInfo:
        """Send an A2S_INFO request and wait for a response.

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        return self._send_until(ClientEventInfo, self._protocol.info)

    def players(self) -> ClientEventPlayers:
        """Send an A2S_PLAYER request and wait for a response.

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        return self._send_until(ClientEventPlayers, self._protocol.players)

    def rules(self) -> ClientEventRules:
        """Send an A2S_RULES request and wait for a response.

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        return self._send_until(ClientEventRules, self._protocol.rules)

    @classmethod
    def from_addr(
        cls,
        host: str,
        port: int,
        timeout: float | None = DEFAULT_TIMEOUT,
        *,
        prefer_ipv4: bool = True,
    ) -> Self:
        """Resolve the given host and create an A2S query.

        :param host: The IPv4 address, IPv6 address, or domain name to query.
        :param port: The port to query.
        :param timeout: The timeout to set on the socket.
        :param prefer_ipv4:
            If True, prefer to resolve hostnames to IPv4 addresses.
            This may still connect the socket to an IPv6 address so if you
            need more control, consider using :func:`socket.getaddrinfo()`
            to manually create a socket and pass it to the constructor.
        :raises OSError: The address could not be resolved.

        """
        addresses = socket.getaddrinfo(
            host,
            port,
            type=socket.SOCK_DGRAM,
            proto=socket.IPPROTO_UDP,
        )
        if not addresses:
            raise OSError("Address could not be resolved")

        if prefer_ipv4:
            addr = next((a for a in addresses if a[0] == socket.AF_INET), addresses[0])
        else:
            addr = addresses[0]

        family, type, proto, _, addr = addr
        sock = socket.socket(family, type, proto)
        sock.settimeout(timeout)
        sock.connect(addr)
        return cls(sock)

    def _create_protocol(self, *, challenge: int) -> A2SClientProtocol:
        """Create the A2S protocol to manage state.

        This method can be overridden by subclasses.

        """
        return A2SClientProtocol(challenge=challenge)

    def _send_until(
        self,
        t: Type[ClientEventT],
        request: Callable[[], ClientPacket],
    ) -> ClientEventT:
        """Use the given request function to generate an outbound packet,
        and wait until the server responds with the given event type.

        This automatically handles challenge responses, re-sending the request
        and waiting again.

        :raises TimeoutError:
            The socket timed out, or the server did not respond with the event.
        :raises ValueError: The server sent a malformed packet.

        """
        self._sock.send(bytes(request()))
        types = (t, ClientEventChallenge)
        remaining = 3

        while remaining > 0 and (events := list(filter_type(types, self._recv()))):
            # Protocol has already stored the latest challenge sequence,
            # but let's filter all of them out from the event cache.
            for challenge in filter_type(ClientEventChallenge, events):
                self._discard(challenge)

            if found := first(t, events):
                self._discard(found)
                return found

            self._sock.send(bytes(request()))
            remaining -= 1

        raise TimeoutError(f"Server failed to respond with {t.__name__}")

    def _recv(self) -> list[ClientEvent]:
        """Read one datagram from the socket and pass it to the protocol.

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        data = self._sock.recv(self.buffer_size)
        return self._receive_datagram(data)

    def _receive_datagram(self, data: bytes) -> list[ClientEvent]:
        """Pass the datagram to the protocol and return any generated events.

        This also sends off any packets that the protocol returns back,
        and stores the events in a local cache for :meth:`events_received()`.

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        self._protocol.receive_datagram(data)
        for packet in self._protocol.packets_to_send():
            self._sock.send(bytes(packet))

        events = self._protocol.events_received()
        self._events.extend(events)
        return events

    def _discard(self, event: ClientEvent) -> None:
        """Discard an event from the cache, if present."""
        with suppress(ValueError):
            self._events.remove(event)


class A2SGoldsource(A2S):
    """A synchronous client for A2S Goldsource queries."""

    def info(self) -> ClientEventGoldsourceInfo:  # type: ignore
        return self._send_until(ClientEventGoldsourceInfo, self._protocol.info)

    def _create_protocol(self, *, challenge: int) -> A2SGoldsourceClientProtocol:
        return A2SGoldsourceClientProtocol(challenge=challenge)
