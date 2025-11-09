"""Type hints for the project.

:author: Shay Hill
:created: 2023-03-22
"""

from collections.abc import Sequence
from typing import Annotated

# points after rounding to nearest integer
IntPoint = tuple[int, int]

# a line segment is a pair of points
IntSegment = tuple[tuple[int, int], tuple[int, int]]

# minx, miny, maxx, maxy
BBox = tuple[float, float, float, float]

# input points
Vec2 = Annotated[Sequence[float], "2D vector"]
Vecs2 = Annotated[Sequence[Vec2], "2D vectors"]

# allow freer input for bounding boxes and svg renders
FloatSegment = tuple[tuple[float, float], tuple[float, float]]
