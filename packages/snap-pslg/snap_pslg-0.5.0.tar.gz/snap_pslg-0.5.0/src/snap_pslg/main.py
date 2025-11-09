"""Clean a PSLG with iterative snap rounding

:author: Shay Hill
:created: 2023-03-22
"""

from __future__ import annotations

import itertools as it
from typing import TYPE_CHECKING

from snap_pslg.helpers import get_unique_items
from snap_pslg.intersections import (
    map_segments_to_pixel_intersections,
    map_segments_to_segment_intersections,
)
from snap_pslg.segments_and_pixels import (
    get_points_and_edges,
    get_segments_and_pixels,
    is_segment,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from snap_pslg.type_hints import IntPoint, IntSegment, Vec2


def _insert_points_at_intersections(segments: set[IntSegment]) -> set[IntSegment]:
    """Insert points at intersections.

    :param segments: A list of segments.
    :return: A list of segments.
    """
    seg2xs = map_segments_to_segment_intersections(segments)
    new_segments: set[IntSegment] = set()
    for seg in segments:
        midpoints = seg2xs.get(seg, set()) - set(seg)
        if midpoints:
            points = [seg[0], *sorted(midpoints), seg[1]]
            for pair in it.pairwise(points):
                new_segments.add(pair)
        else:
            new_segments.add(seg)
    return new_segments


def _clean_segments_and_pixels(
    segments: set[IntSegment], pixels: set[IntSegment]
) -> tuple[set[IntSegment], set[IntSegment]]:
    """Reroute segments through pixel centers.

    :param segments: segments identified as segments
    :param pizels: segments identified as pixels
    :return: A set of segments.

    The only reason the first two args are separate is to make this a bit more
    intuitive. Some of the previous `_is_segment(seg) is True` segments might be
    0-len segments after insert_points_at_intersections or
    reroute_through_pixel_centers. Re-examine all of these.

    * ensure all 0-len segments are in the pixel set
    * no duplicate segments
    * no duplicate pixels
    * no pixels that are also segment endpoints
    """
    segments_and_pixels = segments | pixels
    segments = {s for s in segments_and_pixels if is_segment(s)}
    pixels = segments_and_pixels - segments
    seg_verts = get_unique_items(segments)
    pnt_verts = get_unique_items(pixels) - seg_verts
    return segments, {(x, x) for x in pnt_verts}


def _reroute_through_pixel_centers(
    segments: set[IntSegment], pixels: set[IntSegment]
) -> tuple[set[IntSegment], set[IntSegment]]:
    """Reroute segments through pixel centers.

    :param segments: A set of segments and pixels
    :param pixels: A set of pixels (0-len segments)
    :return: A set of segments.

    If a segment passes through a 1x1 pixel, reroute through the integer intersection
    of that pixel.
    """
    endpoints = {(x, x) for x in get_unique_items(segments)}
    seg2xs = map_segments_to_pixel_intersections(segments | pixels | endpoints)
    new_segments: set[IntSegment] = set()
    for seg in segments:
        if seg in seg2xs:
            points = sorted([*seg, *seg2xs[seg]])
            for pair in it.pairwise(points):
                new_segments.add(pair)
        else:
            new_segments.add(seg)
    return new_segments, pixels


def _snap_round_segments(
    segments: set[IntSegment], pixels: set[IntSegment], max_iterations: int
) -> tuple[set[IntSegment], set[IntSegment]]:
    """Snap segments to pixel centers.

    :param segments: A set of segments
    :param pixels: A set of pixels (0-len segments)
    :return: A set of segments, a set of pixels.

    If a segment passes through a 1x1 pixel, reroute through the integer intersection
    of that pixel.
    """
    for _ in range(max_iterations):
        state_segments = set(segments)
        state_pixels = set(pixels)
        segments = _insert_points_at_intersections(segments)
        segments, pixels = _clean_segments_and_pixels(segments, pixels)
        segments, pixels = _reroute_through_pixel_centers(segments, pixels)
        segments, pixels = _clean_segments_and_pixels(segments, pixels)
        if state_segments == segments and state_pixels == pixels:
            break

    return segments, pixels


def snap_round_pslg(
    points: Iterable[Vec2], edges: Iterable[tuple[int, int]], max_iterations: int = 100
) -> tuple[list[IntPoint], list[tuple[int, int]]]:
    """Perform one iteration of snap rounding.

    :param points: A list of 2D points
    :param edges: A list of edges, each a pair of indices into points
    :param max_iterations: optionally limit number of iterations to perform. By
        default, will try 100 iterations to reach convergence.
    :return: A list of 2D points, a list of edges, each a pair of indices into points

    Some of the points may not have indices. That is fine.
    """
    segments, pixels = get_segments_and_pixels(points, edges)
    segments, pixels = _snap_round_segments(segments, pixels, max_iterations)
    return get_points_and_edges(segments, pixels)
