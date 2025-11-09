"""Intersection tests.

Determine if two segments intersect or if a segment and a pixel intersect.

These DO NOT perform a bounding box test first, because they are all downstream of a
BVH.

:author: Shay Hill
:created: 2023-03-21
"""

from __future__ import annotations

import itertools as it
from collections import defaultdict
from typing import TYPE_CHECKING, Literal

from snap_pslg.bounding_boxes import (
    get_pixel_bbox,
    get_segment_bbox,
    get_segment_or_pixel_bbox,
)
from snap_pslg.bvh import find_potential_intersections
from snap_pslg.segments_and_pixels import get_round_point, is_pixel, is_segment

if TYPE_CHECKING:
    from collections.abc import Iterator

    from snap_pslg.type_hints import IntPoint, IntSegment

Point = tuple[float, float]


def _ccw(a: Point, b: Point, pnt: Point) -> Literal[0, 1, 2]:
    """Get the orientation of three points.

    :param a: first point of a segment
    :param b: second point of a segment
    :param pnt: point to test
    :return:
        0 if all points are colinear
        1 if point is to the right of the segment
        2 if point is to the left of the segment
    """
    # use cross product to determine orientation

    val = (b[1] - a[1]) * (pnt[0] - b[0]) - (b[0] - a[0]) * (pnt[1] - b[1])
    if val == 0:
        return 0
    return 1 if val > 0 else 2


def _do_segs_cross(a: Point, b: Point, c: Point, d: Point) -> bool:
    """Do two line segments AB and CD intersect?

    :param a: first point of segment AB
    :param b: second point of segment AB
    :param c: first point of segment CD
    :param d: second point of segment CD
    :return: True if the line segments intersect, False if the segments do not touch
        and are not connected at their endpoints.

    This does not consider segments that share an endpoint as intersecting.
    """
    if any(pnt_a == pnt_b for pnt_a, pnt_b in it.product((a, b), (c, d))):
        # segments share a point
        return False

    return _ccw(a, c, d) != _ccw(b, c, d) and _ccw(a, b, c) != _ccw(a, b, d)


def _iter_bbox_sides(
    bbox: tuple[float, float, float, float],
) -> Iterator[tuple[tuple[float, float], tuple[float, float]]]:
    """Iterate over the sides of the bounding box.

    :param  bbox: a bounding box (minx, miny, maxx, maxy)
    :yield: (start, end) pairs of the sides of the bounding box
    :return: None
    """
    corners = [
        (bbox[0], bbox[1]),
        (bbox[2], bbox[1]),
        (bbox[2], bbox[3]),
        (bbox[0], bbox[3]),
    ]
    for i in range(4):
        yield corners[i], corners[(i + 1) % 4]


def _do_seg_and_bbox_cross(
    seg_a: Point, seg_b: Point, bbox: tuple[float, float, float, float]
) -> bool:
    """Return True if segment AB intersects with the bounding box.

    :param seg_a: first point of segment AB
    :param seg_b: second point of segment AB
    :param bbox: a bounding box (minx, miny, maxx, maxy)
    """
    sides = ((a, b) for a, b in _iter_bbox_sides(bbox))
    return any(_do_segs_cross(seg_a, seg_b, *side) for side in sides)


def _maybe_get_seg_seg_intersection(
    a: Point, b: Point, c: Point, d: Point
) -> Point | None:
    """Get the intersection of two line segments AB and CD if it exists.

    :param a: first point of segment AB
    :param b: second point of segment AB
    :param c: first point of segment CD
    :param d: second point of segment CD
    :return: the intersection point of the two segments
    """
    if not _do_segs_cross(a, b, c, d):
        return None

    x1, y1 = a
    x2, y2 = b
    x3, y3 = c
    x4, y4 = d

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        # don't worry about this case. Point intersection will handle it later.
        return None

    x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    return x, y


def map_segments_to_segment_intersections(
    segments: set[IntSegment],
) -> dict[IntSegment, set[IntPoint]]:
    """For each segment, create a pixel where it intersects other segments.

    :param segments: A set of segments.
    :return: A dictionary mapping each segment to the set of pixels where it
        intersects other segments, if any. If a segment has no intersections, it will
        be absent from the returned dictionary.
    """
    seg2xs: defaultdict[IntSegment, set[IntPoint]] = defaultdict(set)
    potential_intersections = find_potential_intersections(segments, get_segment_bbox)
    for seg1, seg2 in potential_intersections:
        intersection = _maybe_get_seg_seg_intersection(*seg1, *seg2)
        if intersection is not None:
            round_intersection = get_round_point(intersection)
            seg2xs[seg1].add(round_intersection)
            seg2xs[seg2].add(round_intersection)
    return {**seg2xs}


def map_segments_to_pixel_intersections(
    segments: set[IntSegment],
) -> dict[IntSegment, set[IntPoint]]:
    """For each segment, find the pixels is intersects.

    :param segments: A set of segments.
    :return: A dictionary mapping each segment to the set of 1x1 pixels it intersects.
        If a segment has no intersections, it will be absent from the returned
        dictionary.

    This will create a *lot* of potential intersections because every segment will
    potentially intersect its endpoints.
    """
    seg2xs: defaultdict[IntSegment, set[IntPoint]] = defaultdict(set)
    potential_intersections = find_potential_intersections(
        segments, get_segment_or_pixel_bbox
    )
    for seg1, seg2 in potential_intersections:
        if is_segment(seg1) == is_segment(seg2):
            continue
        the_seg, the_pnt = sorted([seg1, seg2], key=is_pixel)
        if the_pnt[0] in the_seg:
            continue
        if _do_seg_and_bbox_cross(*the_seg, get_pixel_bbox(the_pnt)):
            seg2xs[the_seg].add(the_pnt[0])
    return {**seg2xs}
