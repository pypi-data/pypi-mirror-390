from __future__ import annotations
from collections.abc import Callable
from typing import Literal, Self, override

from jitx.anchor import Anchor
from jitx.feature import Feature, Silkscreen
from jitx.inspect import visit
from jitx.landpattern import Pad
from jitx.shapes import Shape
from jitx.shapes.composites import Bounds, bounds_union
from jitx.shapes.primitive import Circle
from jitx.transform import IDENTITY, Transform
from jitx._structural import Ref

from . import SilkscreenSoldermaskClearanceMixin
from .. import ApplyToMixin, LandpatternGenerator, LandpatternProvider, LineWidthMixin


class MarkerGenerator:
    def create_marker(self, bounds: Bounds, line_width: float) -> Shape:
        raise NotImplementedError("Missing implementation of create_marker")


type MarkerDirection = (
    Literal[Anchor.N] | Literal[Anchor.S] | Literal[Anchor.E] | Literal[Anchor.W]
)


class Pad1MarkerMixin(
    ApplyToMixin,
    SilkscreenSoldermaskClearanceMixin,
    LineWidthMixin,
    LandpatternProvider,
):
    """Pad 1 Marker Mixin"""

    __shape: Shape | MarkerGenerator | None = None
    __side: MarkerDirection | None = None
    __margin: float | None = None

    class PadRef(Ref):
        def __init__(self, pad: Pad):
            self.pad = pad

    __pad_1: PadRef | None = None

    @override
    def _build(self):
        if self.__pad_1:
            self.__pad_1.pad.__pad_1_marker = None
        super()._build()

    @override
    def _build_decorate(self):
        super()._build_decorate()

        if self.__shape is not None:
            try:
                pad_xform, first = next(iter(self._applies_to_transformed_objects(Pad)))
            except StopIteration:
                raise ValueError("No pads found in landpattern") from None
            (tx, ty), rot, _scale = (pad_xform * (first.transform or IDENTITY)).trs
            if self.__side is None:
                if abs(tx) > abs(ty):
                    if tx < 0:
                        side = Anchor.W
                    else:
                        side = Anchor.E
                else:
                    if ty < 0:
                        side = Anchor.S
                    else:
                        side = Anchor.N
            else:
                side = self.__side

            minx, miny, maxx, maxy = bounds_union(
                ((trace.transform or IDENTITY) * feat.shape).to_shapely().bounds
                for trace, feat in visit(first, Feature)
            )
            match side:
                case Anchor.W:
                    minx, miny, maxx, maxy = miny, minx, maxy, maxx
                case Anchor.E:
                    minx, miny, maxx, maxy = miny, minx, maxy, maxx
            if self.__margin is None:
                # assume there's a line here to skip over.
                margin = 2 * self._line_width + self._silkscreen_soldermask_clearance
            else:
                margin = max(self.__margin, self._silkscreen_soldermask_clearance)

            offset = Transform.translate(0, maxy + margin)
            match side:
                case Anchor.W:
                    offset = Transform.rotate(90 - rot) * offset
                case Anchor.S:
                    offset = Transform.rotate(180 - rot) * offset
                case Anchor.E:
                    offset = Transform.rotate(270 - rot) * offset
            if isinstance(self.__shape, MarkerGenerator):
                bounds = minx, miny, maxx, maxy
                shape = self.__shape.create_marker(bounds, self._line_width)
            else:
                shape = self.__shape
            first.__pad_marker = Silkscreen(offset * shape)
            self.__pad_1 = self.PadRef(first)

    def pad_1_marker(
        self, shape: Shape | MarkerGenerator | Callable[[], MarkerGenerator]
    ) -> Self:
        """Add a pad 1 marker to the landpattern. The shape will be placed in a
        coordinate system relative to the outside edge of the first pad, with
        the positive y-axis pointing away from the pad. Thus the shape should
        not extend to negative y values."""
        if callable(shape):
            self.__shape = shape()
        else:
            self.__shape = shape
        return self

    def pad_1_marker_direction(
        self, direction: MarkerDirection | None = None, margin: float | None = None
    ) -> Self:
        """Set the side of the pad 1 marker. If not set, the marker will be
        placed on the side of the first pad that appears to be facing away from
        the package.

        Args:
            direction: the direction to place the marker
            margin: the margin between the marker and the pad
        """
        self.__side = direction
        self.__margin = margin
        return self


class Pad1Marker(Pad1MarkerMixin, LandpatternGenerator):
    """Convenience base class to create a pad 1 circle marker by default."""

    @override
    def __base_init__(self):
        super().__base_init__()
        self.pad_1_marker(CircleMarker)


class CircleMarker(MarkerGenerator):
    @override
    def create_marker(self, bounds: Bounds, line_width: float) -> Shape:
        return Circle(radius=line_width).at(0, line_width)
