import logging
import socket
from typing import Callable, Self, Type

from little_a2s.client.constants import DEFAULT_TIMEOUT
from little_a2s.client.types import Address, ClientEventT, filter_type, first
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

log = logging.getLogger(__name__)


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

    This class is not thread-safe.

    :param sock:
        The UDP socket to send and receive queries from.
        The socket can be connected to a remote address beforehand
        with :meth:`~socket.socket.connect()`, if you want to skip
        ``addr`` arguments in send methods. You may also want to
        set a timeout with :meth:`~socket.socket.settimeout()`.
        Alternatively, use :meth:`from_addr()`, :meth:`from_ipv4()`,
        or :meth:`from_ipv6()` to construct the socket for you.

    .. versionadded:: 0.2.0

    .. versionchanged:: 0.5.0

        Removed the ``challenge=`` parameter.

    .. versionchanged:: 0.5.0

        Removed the ``events_received()`` method.

    """

    buffer_size = 32768  # probably overkill?
    _protocols: dict[Address | None, A2SClientProtocol]

    def __init__(self, sock: socket.socket) -> None:
        if sock.type != socket.SOCK_DGRAM:
            raise ValueError("Socket type must be SOCK_DGRAM")

        self._sock = sock
        self._protocols = {}

    def __enter__(self) -> Self:
        self._sock.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, tb) -> None:
        return self._sock.__exit__(exc_type, exc_val, tb)

    def info(self, addr: Address | None = None) -> ClientEventInfo:
        """Send an A2S_INFO request and wait for a response.

        .. versionchanged:: 0.5.0

            addr can now be a positional argument.

        :param addr:
            The address to send the request to.
            Does not apply if socket is already connected to an address,
            such as from :meth:`from_addr()`.

            .. versionadded:: 0.4.0

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        proto = self._get_protocol(addr)
        return self._send_until(ClientEventInfo, proto.info, addr)

    def players(self, addr: Address | None = None) -> ClientEventPlayers:
        """Send an A2S_PLAYER request and wait for a response.

        .. versionchanged:: 0.5.0

            addr can now be a positional argument.

        :param addr:
            The address to send the request to.
            Does not apply if socket is already connected to an address,
            such as from :meth:`from_addr()`.

            .. versionadded:: 0.4.0

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        proto = self._get_protocol(addr)
        return self._send_until(ClientEventPlayers, proto.players, addr)

    def rules(self, addr: Address | None = None) -> ClientEventRules:
        """Send an A2S_RULES request and wait for a response.

        .. versionchanged:: 0.5.0

            addr can now be a positional argument.

        :param addr:
            The address to send the request to.
            Does not apply if socket is already connected to an address,
            such as from :meth:`from_addr()`.

            .. versionadded:: 0.4.0

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        proto = self._get_protocol(addr)
        return self._send_until(ClientEventRules, proto.rules, addr)

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

            .. versionadded:: 0.2.1
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

    @classmethod
    def from_ipv4(cls, timeout: float | None = DEFAULT_TIMEOUT) -> Self:
        """Create an A2S query with a UDP IPv4 socket not connected to any address.

        This allows you to use the same socket with ``addr`` arguments::

            with A2S.from_ipv4() as a2s:
                info = a2s.info(("127.0.0.1", 2303))
                info = a2s.info(("127.0.0.1", 27015))

        :param timeout: The timeout to set on the socket.

        .. versionadded:: 0.4.0

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(timeout)
        return cls(sock)

    @classmethod
    def from_ipv6(cls, timeout: float | None = DEFAULT_TIMEOUT) -> Self:
        """Create an A2S query with a UDP IPv6 socket not connected to any address.

        This allows you to use the same socket with ``addr`` arguments::

            with A2S.from_ipv6() as a2s:
                info = a2s.info(("::1", 2303))
                info = a2s.info(("::1", 27015))

        :param timeout: The timeout to set on the socket.

        .. versionadded:: 0.4.0

        """
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(timeout)
        return cls(sock)

    def _get_protocol(self, addr: Address | None) -> A2SClientProtocol:
        """Get the A2S protocol for the given address, creating a new one
        if it doesn't already exist.

        :param addr: The address to bind to, or None for the default protocol.

        """
        # NOTE: not thread-safe!
        proto = self._protocols.get(addr)
        if proto is not None:
            return proto

        proto = self._create_protocol()
        self._protocols[addr] = proto
        return proto

    def _create_protocol(self) -> A2SClientProtocol:
        """Create the A2S protocol to manage state.

        This method can be overridden by subclasses.

        """
        return A2SClientProtocol()

    def _send_until(
        self,
        t: Type[ClientEventT],
        request: Callable[[], ClientPacket],
        addr: Address | None,
    ) -> ClientEventT:
        """Use the given request function to generate an outbound packet,
        and wait until the server responds with the given event type.

        This automatically handles challenge responses, re-sending the request
        and waiting again.

        :raises TimeoutError:
            The socket timed out, or the server did not respond with the event.
        :raises ValueError: The server sent a malformed packet.

        """
        self._send(bytes(request()), addr)
        types = (t, ClientEventChallenge)
        remaining = 3

        while remaining > 0 and (events := list(filter_type(types, self._recv(addr)))):
            if found := first(t, events):
                return found

            self._send(bytes(request()), addr)
            remaining -= 1

        raise TimeoutError(f"Server failed to respond with {t.__name__}")

    def _send(self, data: bytes, addr: Address | None) -> int:
        if addr is not None:
            return self._sock.sendto(data, addr)
        else:
            return self._sock.send(data)

    def _recv(self, addr: Address | None) -> list[ClientEvent]:
        """Read one datagram from the socket and pass it to the protocol.

        If address is not None, this may call :meth:`~socket.socket.recvfrom()`
        multiple times until a datagram from the given address is received.

        :param addr: The address to wait for a datagram from.
        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        # NOTE: not thread-safe!
        data, recv_addr = self._sock.recvfrom(self.buffer_size)
        events = self._receive_datagram(data, addr and recv_addr)

        while not events or addr and addr != recv_addr:
            data, recv_addr = self._sock.recvfrom(self.buffer_size)
            events = self._receive_datagram(data, addr and recv_addr)

        return events

    def _receive_datagram(self, data: bytes, addr: Address | None) -> list[ClientEvent]:
        """Pass the datagram to the protocol and return any generated events.

        :raises TimeoutError: The socket timed out.
        :raises ValueError: The server sent a malformed packet.

        """
        proto = self._protocols.get(addr)
        if proto is None:
            log.debug("Ignoring data from unexpected address %s", addr)
            return []

        proto.receive_datagram(data)
        for packet in proto.packets_to_send():
            self._send(bytes(packet), addr)

        return proto.events_received()


class A2SGoldsource(A2S):
    """A synchronous client for A2S Goldsource queries."""

    def info(self, addr: Address | None = None) -> ClientEventGoldsourceInfo:  # type: ignore
        proto = self._get_protocol(addr)
        return self._send_until(ClientEventGoldsourceInfo, proto.info, addr)

    def _create_protocol(self) -> A2SGoldsourceClientProtocol:
        return A2SGoldsourceClientProtocol()
