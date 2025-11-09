"""Create slightly undersized bounding boxes segments and pixels.

:author: Shay Hill
:created: 2023-03-22
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from snap_pslg.segments_and_pixels import is_pixel

if TYPE_CHECKING:
    from snap_pslg.type_hints import BBox, FloatSegment, IntSegment


def get_segment_bbox(segment: IntSegment | FloatSegment) -> BBox:
    """Create a slightly undersized bounding box for a segment.

    :param segment: A two-tuple of integer or float two-tuples.
    :return: A four-tuple of floats (min_x, min_y, max_x, max_y).

    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED

    This is slightly undersized to skip some of the bounding box intersections with
    sequential segments or adjacent pixels. Intersections or near intersections where
    one point is on or very near a segment will be identified by the T-junction test.
    You will end up with a degenerate bounding box if a segment is 0 len or perfectly
    horizontal or vertical. There is no need to worry about degenerate bounding
    boxes. They will not effect anything.
    """
    (ax, ay), (bx, by) = segment
    return (
        math.nextafter(min(ax, bx), math.inf),
        math.nextafter(min(ay, by), math.inf),
        math.nextafter(max(ax, bx), -math.inf),
        math.nextafter(max(ay, by), -math.inf),
    )


def get_pixel_bbox(pixel: IntSegment | FloatSegment) -> BBox:
    """Create a 1x1 square around a point.

    :param pixel: An integer or float two-tuple
    :return: A four-tuple of floats (x-0.5, y-0.5, x+0.5, y+0.5).

    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED
    THIS IS SLIGHTLY UNDERSIZED

    This is slightly undersized to skip intersection tests for adjacent pixels.
    """
    x, y = pixel[0]
    return (
        math.nextafter(x - 0.5, math.inf),
        math.nextafter(y - 0.5, math.inf),
        math.nextafter(x + 0.5, -math.inf),
        math.nextafter(y + 0.5, -math.inf),
    )


def get_segment_or_pixel_bbox(segment_or_pixel: IntSegment) -> BBox:
    """Get the bounding box for a segment or a pixel.

    :param segment_or_pixel: An integer two-tuple.
    :return: A four-tuple of floats (min_x, min_y, max_x, max_y).
    """
    if is_pixel(segment_or_pixel):
        return get_pixel_bbox(segment_or_pixel)
    return get_segment_bbox(segment_or_pixel)
