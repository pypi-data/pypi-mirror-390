"""Create an svg from a PSLG.

:author: Shay Hill
:created: 2023-03-23
"""

# Ignore missing module source for optional dependency svg-ultralight.
# `# type: ignore` on the import line gets flagged as unnecessary when I have
# svg-ultralight installed for testing.
# pyright: reportMissingModuleSource=false

from __future__ import annotations

try:
    from svg_ultralight import new_sub_element, new_svg_root, write_svg
except ModuleNotFoundError as exc:
    MSG = "`pip install svg-ultralight` to use snap_pslg.view_pslg module"
    raise ModuleNotFoundError(MSG) from exc

from typing import TYPE_CHECKING

from snap_pslg.bounding_boxes import get_pixel_bbox

if TYPE_CHECKING:
    from pathlib import Path

    from snap_pslg.type_hints import Vecs2

POINT_ATTRIB = {"fill": "red", "opacity": 0.5}
EDGE_ATTRIB = {
    "stroke": "gray",
    "stroke-linecap": "round",
    "stroke-width": 0.25,
    "opacity": 0.5,
}
TEXT_ATTRIB = {"font-size": 0.35, "fill": "black", "font-family": "monospace"}


def _bbox_to_xywh(
    bbox: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """Return a bbox as x, y, width, height."""
    x, y, x2, y2 = bbox
    return x, y, x2 - x, y2 - y


def write_svg_from_pslg(
    svg_path: Path | str, points: Vecs2, edges: list[tuple[int, int]]
) -> None:
    """Return an svg element for a vertex."""
    xs, ys = zip(*points, strict=True)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    x, y, width, height = _bbox_to_xywh((min_x, min_y, max_x, max_y))
    root = new_svg_root(x, y, width, height, pad_=1)
    for x, y in points:
        rx, ry, width, height = _bbox_to_xywh(get_pixel_bbox(((x, y), (x, y))))
        _ = new_sub_element(
            root, "rect", x=rx, y=ry, width=width, height=height, **POINT_ATTRIB
        )
        _ = new_sub_element(root, "text", x=rx, y=y, text=f"{x:.1f}", **TEXT_ATTRIB)
        _ = new_sub_element(
            root, "text", x=rx, y=y + 0.4, text=f"{y:.1f}", **TEXT_ATTRIB
        )
    for a, b in edges:
        x1, y1 = points[a]
        x2, y2 = points[b]
        _ = new_sub_element(root, "line", x1=x1, y1=y1, x2=x2, y2=y2, **EDGE_ATTRIB)
    _ = write_svg(svg_path, root)
