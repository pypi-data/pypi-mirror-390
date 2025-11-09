"""As of right now, one helper function.

:author: Shay Hill
:created: 2023-03-22
"""

from collections.abc import Hashable, Iterable
from typing import TypeVar

_HashableT = TypeVar("_HashableT", bound=Hashable)


def get_unique_items(groups: Iterable[Iterable[_HashableT]]) -> set[_HashableT]:
    """Get a set of shared items from a group of iterables.

    :param groups: A interable of iterable of hashable items. e.g., [[1, 2], [2, 3]]
    :return: A set of unique items. e.g., {1, 2, 3}
    """
    union: set[_HashableT] = set()
    for group in groups:
        union |= set(group)
    return union
