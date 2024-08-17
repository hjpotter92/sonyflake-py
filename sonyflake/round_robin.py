from __future__ import annotations

from itertools import cycle
from typing import Iterable, Iterator


class RoundRobin(Iterator[int]):
    """Round-robin iterator for cycling through multiple ID generators.

    Used for generating ids at rate more than 256ids/10msec.

    Example:
    >>> from sonyflake import RoundRobin, SonyFlake, random_machine_ids
    >>> sf = RoundRobin([SonyFlake(machine_id=_id) for _id in random_machine_ids(10)])
    >>> %timeit next(sf)
    """

    _id_generators: cycle[Iterator[int]]
    __slots__ = ("_id_generators",)

    def __init__(self, id_generators: Iterable[Iterator[int]]) -> None:
        self._id_generators = cycle(id_generators)

    def __next__(self) -> int:
        return next(next(self._id_generators))

    next_id = __next__
