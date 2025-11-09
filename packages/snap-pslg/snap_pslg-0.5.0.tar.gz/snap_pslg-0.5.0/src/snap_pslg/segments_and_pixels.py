"""Convert input to integer segments and pixels.

:author: Shay Hill
:created: 2023-03-22
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Annotated

from snap_pslg.helpers import get_unique_items

if TYPE_CHECKING:
    from collections.abc import Iterable

    from snap_pslg.type_hints import IntPoint, IntSegment, Vec2


def is_pixel(pixel_or_segment: IntSegment) -> bool:
    """All pixels are 0-length segments."""
    return pixel_or_segment[0] == pixel_or_segment[1]


def is_segment(pixel_or_segment: IntSegment) -> bool:
    """A segment with a length is not a pixel."""
    return not is_pixel(pixel_or_segment)


def _get_floor_point(point: Annotated[Iterable[float], (2,)]) -> tuple[int, int]:
    """Floor floating-point coordinates to integers.

    Floor the input coordinates because the result will be laid out in pixels. If an
    image is 2 pixels wide, these are 0 and 1. If a vector in that image has a value
    of 1.999, that vector will appear in pixel 1.  There is no pixel 2 to which it
    could be rounded.

    Any coordinates created after init will be interpolated and rounded (not floored)
    to the nearest integer.
    """
    x, y = point
    return math.floor(x), math.floor(y)


def get_round_point(point: Annotated[Iterable[float], (2,)]) -> tuple[int, int]:
    """Round new points to the nearest integer."""
    x, y = point
    return round(x), round(y)


def get_segments_and_pixels(
    points: Iterable[Vec2], edges: Iterable[tuple[int, int]]
) -> tuple[set[IntSegment], set[IntSegment]]:
    """From floating point veciors and index pairs, yield integer segments.

    :param points: Floating point x,y vectors.
    :param edges: Index pairs.
    :return:
        segments -> two-tuple of integer two-tuples in lexigraphical order.
        pixels -> two-tuple of identical integer two-tuples.

    Pixels are "free" coordinates not used in any segment. I represent these as
    0-length segments.

    The return value is clean, meaning there are

    * no duplicate segments
    * no duplicate pixels
    * no pixels that are also segment endpoints
    """
    segments: set[IntSegment] = set()
    pixels: set[IntSegment] = set()

    round_points = [_get_floor_point(p) for p in points]
    seen: set[int] = set()
    for edge in edges:
        seen |= set(edge)
        seg_a, seg_b = sorted(round_points[x] for x in edge)
        segments.add((seg_a, seg_b))
    for point in (p for i, p in enumerate(round_points) if i not in seen):
        pixels.add((point, point))
    return segments, pixels


def get_points_and_edges(
    segments: set[IntSegment], pixels: set[IntSegment]
) -> tuple[list[IntPoint], list[tuple[int, int]]]:
    """Convert segments and pixels back to a point list and index tuples.

    :param segments: segments output from snap_round_pslg
    :param pixels: pixels output from snap_round_pslg
    :return: points, edges
    """
    points = list(get_unique_items(segments | pixels))
    point2index = {p: i for i, p in enumerate(points)}
    return points, [(point2index[a], point2index[b]) for a, b in segments]
