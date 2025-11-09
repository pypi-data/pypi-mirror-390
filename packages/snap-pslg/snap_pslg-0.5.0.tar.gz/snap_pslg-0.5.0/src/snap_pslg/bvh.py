"""A BVH implementation.

This module finds potential intersections using a bounding volume hierarchy. The main
public function is `find_potential_intersections`. Internally, this wraps input
objects in BoundObj instances and creates BVHNode instances, but these instances are
not necessarily meant to "escape" this module. The classes are public, and there are
a few public functions which return instances of these classes, but those are
primarity for extension and experimentation.

The primary purpose is to pass:

* a list of anything
* a function to create a bounding box for each item in that list

And get back:

* at iterator of item pairs which may intersect

If the items passes have a bbox attribute and no get_bbox function is provided, then
that attribute will be converted to a tuple and used by the BVH. Bounding boxes must
be of the form (min_x, min_y, ..., max_x, max_y, ...) for any number of dimensions.

I suggest padding your bounding boxes with

(math.nextafter(min_x, -math.inf), ..., math.nextafter(max_x, math.inf), ...)

to avoid floating point errors.

:author: Shay Hill
:created: 2023-03-21
"""

from __future__ import annotations

import dataclasses
import itertools as it
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Annotated, Generic, TypeAlias, TypeVar, cast

_BBox: TypeAlias = Annotated[tuple[float, ...], "min_x, min_y, ..., max_x, max_y, ..."]
_T = TypeVar("_T")

_SequenceT = TypeVar("_SequenceT", bound=Sequence[object])


def _default_get_bbox(obj: object) -> _BBox:
    """Return a bbox attribute if no get_bbox function is provided."""
    if hasattr(obj, "bbox"):
        return (
            obj.bbox  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        )
    msg = "No get_bbox function provided and object has no bbox attribute."
    raise AttributeError(msg)


def _split_sequence(seq: _SequenceT) -> tuple[_SequenceT, _SequenceT]:
    """Split a tuple into two relately equal length tuples.

    A BBox split this way will be split into min and max values.
    (min_x, min_y, ...), (max_x, max_y, ...)
    """
    mid_index = len(seq) // 2
    left = cast("_SequenceT", seq[:mid_index])
    right = cast("_SequenceT", seq[mid_index:])
    return left, right


def _get_bbox_union(*bboxes: _BBox) -> _BBox:
    """Return the union of the bounding boxes."""
    if len(bboxes) == 1:
        return bboxes[0]
    all_mins, all_maxs = zip(*(_split_sequence(b) for b in bboxes), strict=True)
    return tuple(
        [min(x) for x in zip(*all_mins, strict=True)]
        + [max(x) for x in zip(*all_maxs, strict=True)]
    )


def _get_bbox_measurements(bbox: _BBox) -> list[float]:
    """Return the measurements of the bounding box."""
    mins, maxs = _split_sequence(bbox)
    return [y - x for x, y in zip(mins, maxs, strict=True)]


@dataclasses.dataclass
class BoundObj(Generic[_T]):
    """Anything and a bbox attribute"""

    obj: _T
    bbox: _BBox
    centroid: list[float] = dataclasses.field(init=False, compare=False)

    def __post_init__(self) -> None:
        """Calculate the centroid of the bounding box."""
        mins, maxs = _split_sequence(self.bbox)
        self.centroid = [(x + y) / 2 for x, y in zip(mins, maxs, strict=True)]


class BVHNode(Generic[_T]):
    """One node in a Bounding Volume Hierarchy tree."""

    def __init__(
        self,
        bbox: _BBox,
        left: BVHNode[_T] | None = None,
        right: BVHNode[_T] | None = None,
        obj: _T | None = None,
    ) -> None:
        """Initialize the node.

        Store left and right for non-leaf nodes
        Store obj for leaf nodes

        Initialize a flag, has_potential_unidentified_self_intersections, to be set
        to false after the first comparison of self.left and self.right.
        """
        self.left = left
        self.right = right
        self.bbox = bbox
        self._obj = obj
        self.has_potential_unidentified_self_intersections = not self.is_leaf

    def maybe_branch(
        self,
    ) -> tuple[BVHNode[_T]] | tuple[BVHNode[_T] | None, BVHNode[_T] | None]:
        """Return the node to descend to if this node is not a leaf.

        :return: The node to descend to if this node is not a leaf, else self.
        """
        if self.is_leaf:
            return (self,)
        return self.left, self.right

    @property
    def is_leaf(self) -> bool:
        """If this node a leaf node.

        :return: True if node is a leaf.
        """
        return self.left is None and self.right is None

    @property
    def obj(self) -> _T:
        """The object stored in leaf nodes.

        :return: The object stored in a leaf node.
        :raises AttributeError: If this node is not a leaf.
        """
        if self._obj is None:
            msg = "This node is not a leaf."
            raise AttributeError(msg)
        return self._obj


def _build_bvh_from_bound_objects(bound_objects: list[BoundObj[_T]]) -> BVHNode[_T]:
    """Build a BVH from a list of bound objects.

    :param bound_objects: A list of _BoundObject instances created in build_bvh.
    :return: A BVHNode root node. The bounds (attached bounding boxes) are discarded.
    """
    bbox = _get_bbox_union(*(x.bbox for x in bound_objects))

    if len(bound_objects) == 1:
        return BVHNode(bbox, obj=bound_objects[0].obj)

    # split objects into two lists
    dims = _get_bbox_measurements(bbox)
    axis = dims.index(max(dims))
    bound_objects.sort(key=lambda x: (x.centroid[axis], x.centroid))
    left_objects, right_objects = _split_sequence(bound_objects)

    left = _build_bvh_from_bound_objects(left_objects)
    right = _build_bvh_from_bound_objects(right_objects)
    return BVHNode(bbox, left=left, right=right)


def build_bvh(
    objs: Iterable[_T], get_bbox: Callable[[_T], _BBox] = _default_get_bbox
) -> BVHNode[_T]:
    """Build a BVH from a list of objects.

    :param objs: A list of objects to build the BVH from.
    :param get_bbox: A function that takes an object and returns a bounding box. If
        the object has a bbox attribute, that attribute will be used if no get_bbox
        function is provided.
    :return: A BVHNode root node.

    This function will wrap input objects in temporary _BoundObject instances. The
    bounding boxes are retained in the leaf nodes, but this wrapper is discarded
    before returning the BVH.
    """
    bound_objects = [BoundObj(x, get_bbox(x)) for x in objs]
    return _build_bvh_from_bound_objects(bound_objects)


def _do_bboxes_intersect(bbox_a: _BBox, bbox_b: _BBox) -> bool:
    """Return True if two bounding boxes of any dimensionality intersect."""
    min_a, max_a = _split_sequence(bbox_a)
    min_b, max_b = _split_sequence(bbox_b)
    if any(a > b for a, b in zip(min_a, max_b, strict=True)):
        return False
    return not any(a < b for a, b in zip(max_a, min_b, strict=True))


def find_bvh_intersecting_nodes(
    left: BVHNode[_T] | None, right: BVHNode[_T] | None = None
) -> Iterator[tuple[BVHNode[_T], BVHNode[_T]]]:
    """Yield all pairs of leaf nodes with intersecting bounding boxes.

    :param left: The root node or the left node of a parent node
    :param right: The right node of a parent node.
    :yield: pairs of leaf nodes that may intersect.
    :return: None

    Pass just the root node to kick this off. The function will recurse into the root
    node's children.
    """
    nodes = [x for x in (left, right) if x is not None]
    if not nodes:
        return

    for node in (n for n in nodes if n.has_potential_unidentified_self_intersections):
        yield from find_bvh_intersecting_nodes(node.left, node.right)
        node.has_potential_unidentified_self_intersections = False

    # left-right intersections
    if len(nodes) == 1 or not _do_bboxes_intersect(nodes[0].bbox, nodes[1].bbox):
        return
    if nodes[0].is_leaf and nodes[1].is_leaf:
        yield nodes[0], nodes[1]
        return
    for pair in it.product(nodes[0].maybe_branch(), nodes[1].maybe_branch()):
        yield from find_bvh_intersecting_nodes(*pair)


def find_bvh_intersections(
    left: BVHNode[_T] | None, right: BVHNode[_T] | None = None
) -> Iterator[tuple[_T, _T]]:
    """Yield pairs of objects with intersecting bounding boxes.

    :param left: The root node or the left node of a parent node
    :param right: The right node of a parent node.
    :yield: pairs of objects that may intersect.
    :return: None
    """
    for left_node, right_node in find_bvh_intersecting_nodes(left, right):
        yield left_node.obj, right_node.obj


def find_potential_intersections(
    objs: Iterable[_T], get_bbox: Callable[[_T], _BBox] = _default_get_bbox
) -> Iterator[tuple[_T, _T]]:
    """Yield pairs of objects with intersecting bounding boxes.

    :param objs: A list of objects to build the BVH from.
    :param get_bbox: A function that takes an object and returns a bounding box. If
        the object has a bbox attribute, that attribute will be used if no get_bbox
        function is provided.
    :yield: pairs of objs that may intersect.
    :return: None
    """
    bvh = build_bvh(objs, get_bbox)
    yield from find_bvh_intersections(bvh)
