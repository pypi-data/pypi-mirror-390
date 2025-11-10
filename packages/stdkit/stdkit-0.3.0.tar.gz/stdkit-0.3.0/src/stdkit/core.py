__all__ = [
    "flatten",
    "max_signed_value",
]

from collections.abc import Iterable, Iterator, Sequence
from typing import Any


def flatten(*items: Any | Iterable[Any]) -> Iterator[Any]:
    """Flatten iterable of items.

    Examples
    --------
    >>> from stdkit import core
    >>> list(core.flatten([[1, 2], *[3, 4], [5]]))
    [1, 2, 3, 4, 5]

    >>> list(core.flatten([1, (2, 3)], 4, [], [[[5]], 6]))
    [1, 2, 3, 4, 5, 6]

    >>> list(core.flatten(["one", 2], 3, [(4, "five")], [[["six"]]], "seven", []))
    ['one', 2, 3, 4, 'five', 'six', 'seven']
    """

    def _flatten(items):
        for item in items:
            if isinstance(item, (Iterator, Sequence)) and not isinstance(item, str):
                yield from _flatten(item)
            else:
                yield item

    return _flatten(items)


def max_signed_value(num_bits: int, /) -> int:
    """Return the maximum signed integer value for the specified bit width.

    Examples
    --------
    >>> # compute the maximum signed value for a 32-bit integer
    >>> from stdkit import core
    >>> core.max_signed_value(32)
    2147483647
    """
    if not isinstance(num_bits, int):
        raise TypeError(f"type(num_bits)={type(num_bits).__name__!r} - expected int")

    if num_bits < 2:
        raise ValueError(f"{num_bits=!r} - expected >= 2 for signed range")

    return (1 << (num_bits - 1)) - 1
