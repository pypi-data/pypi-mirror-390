from typing import Iterable, Iterator, Type, TypeVar

from little_a2s.events import ClientEvent

Address = tuple[str, int] | tuple[str, int, int, int] | tuple[int, bytes]
T = TypeVar("T")
ClientEventT = TypeVar("ClientEventT", bound=ClientEvent)


def filter_type(
    t: Type[T] | tuple[Type[T], ...],
    it: Iterable[object],
    /,
) -> Iterator[T]:
    """Filter through an iterable for elements of the given type.

    .. versionadded:: 0.2.0

    """
    for x in it:
        if isinstance(x, t):
            yield x


def first(t: Type[T] | tuple[Type[T], ...], it: Iterable[object], /) -> T | None:
    """Return the first element of the given type in an iterable.

    .. versionadded:: 0.2.0

    """
    return next(filter_type(t, it), None)


def last(t: Type[T] | tuple[Type[T], ...], it: Iterable[object], /) -> T | None:
    """Return the last element of the given type in an iterable.

    .. versionadded:: 0.2.0

    """
    x = None
    for x in filter_type(t, it):
        pass
    return x
