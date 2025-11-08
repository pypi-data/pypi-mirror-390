from .client import (
    A2S as A2S,
    A2SGoldsource as A2SGoldsource,
    AsyncA2S as AsyncA2S,
    AsyncA2SGoldsource as AsyncA2SGoldsource,
    filter_type as filter_type,
    first as first,
    last as last,
)
from .events import (
    ClientEvent as ClientEvent,
    ClientEventChallenge as ClientEventChallenge,
    ClientEventGoldsourceInfo as ClientEventGoldsourceInfo,
    ClientEventInfo as ClientEventInfo,
    ClientEventPlayers as ClientEventPlayers,
    ClientEventRules as ClientEventRules,
    Environment as Environment,
    Event as Event,
    ExtraInfo as ExtraInfo,
    GoldsourceMod as GoldsourceMod,
    GoldsourceModDLL as GoldsourceModDLL,
    GoldsourceModType as GoldsourceModType,
    Player as Player,
    ServerType as ServerType,
    VAC as VAC,
    Visibility as Visibility,
)
from .headers import (
    Compression as Compression,
    Header as Header,
    HeaderType as HeaderType,
    MultiGoldsourceHeader as MultiGoldsourceHeader,
    MultiHeader as MultiHeader,
    SimpleHeader as SimpleHeader,
)
from .packets import (
    ClientPacket as ClientPacket,
    ClientPacketInfo as ClientPacketInfo,
    ClientPacketPlayers as ClientPacketPlayers,
    ClientPacketRules as ClientPacketRules,
    Packet as Packet,
)
from .protocol import (
    A2SClientProtocol as A2SClientProtocol,
    A2SGoldsourceClientProtocol as A2SGoldsourceClientProtocol,
    MultiPartResponse as MultiPartResponse,
)
from .reader import Readable as Readable, Reader as Reader
from .rules import (
    Arma3DLC as Arma3DLC,
    Arma3Difficulty as Arma3Difficulty,
    Arma3Mod as Arma3Mod,
    Arma3Rules as Arma3Rules,
)


def _get_version() -> str:
    from importlib.metadata import version

    return version(_dist_name)


_dist_name = "little-a2s"
__version__ = _get_version()
