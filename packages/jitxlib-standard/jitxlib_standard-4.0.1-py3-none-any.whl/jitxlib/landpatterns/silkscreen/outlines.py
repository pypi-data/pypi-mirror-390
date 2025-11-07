from __future__ import annotations
from collections.abc import Sequence
from enum import IntEnum
from typing import Self, overload, override

from jitx.feature import Silkscreen, Soldermask
from jitx.layerindex import Side
from jitx.shapes import Shape
from jitx.shapes.composites import Bounds, bounds_area, buffer_bounds
from jitx.shapes.shapely import ShapelyGeometry
import shapely

from . import SilkscreenSoldermaskClearanceMixin
from .. import ApplyToMixin, LandpatternGenerator, LineWidthMixin
from ..ipc import DensityLevelMixin
from ..package import PackageBodyMixin


from logging import getLogger

logger = getLogger(__name__)


class SilkscreenLine(IntEnum):
    """Silkscreen Edge"""

    Top = 1
    Bottom = 2
    Left = 4
    Right = 8
    Vertical = Left | Right
    Horizontal = Top | Bottom
    Perimeter = Horizontal | Vertical
    XAxis = 16
    YAxis = 32


class SilkscreenLineGenerator:
    __line: int = SilkscreenLine.Perimeter
    __corner: float = 0
    __line_offset: float = 0

    def silkscreen_line(self, line: SilkscreenLine | int, offset: float = 0):
        """Set the silkscreen edge to draw.

        Args:
            line: The silkscreen edge to use.
            offset: Offset the line by this amount. Mainly for aesthetic
            reasons. Positive is outwards.

        Returns:
            self for method chaining.
        """
        if not 0 < line < 64:
            raise ValueError("Invalid silkscreen edge")
        self.__line = line
        self.__line_offset = offset
        return self

    def silkscreen_corner(self, corner: float = 0.15):
        """Set the silkscreen corner ratio"""
        self.__corner = corner
        return self

    def _silkscreen_line(self, bounds: Bounds, line_width: float) -> Shape:
        Top = SilkscreenLine.Top
        Bottom = SilkscreenLine.Bottom
        Left = SilkscreenLine.Left
        Right = SilkscreenLine.Right
        XAxis = SilkscreenLine.XAxis
        YAxis = SilkscreenLine.YAxis

        minx, miny, maxx, maxy = bounds
        minx -= self.__line_offset
        miny -= self.__line_offset
        maxx += self.__line_offset
        maxy += self.__line_offset

        multiline = []
        if self.__line & SilkscreenLine.Perimeter:
            perimeter = (
                ((maxx, maxy), (minx, maxy)),
                ((minx, maxy), (minx, miny)),
                ((minx, miny), (maxx, miny)),
                ((maxx, miny), (maxx, maxy)),
            )
            pts = []
            for idx, elem in enumerate((Top, Left, Bottom, Right)):
                if self.__line & elem:
                    if not pts:
                        pts.extend(perimeter[idx])
                    else:
                        pts.append(perimeter[idx][1])
                elif pts:
                    multiline.append(pts)
                    pts = []
            if pts:
                multiline.append(pts)

        if self.__line & (XAxis | YAxis):
            midx = (minx + maxx) / 2.0
            midy = (miny + maxy) / 2.0
            axes = (
                ((minx, midy), (maxx, midy)),
                ((midx, miny), (midx, maxy)),
            )
            for idx, elem in enumerate((XAxis, YAxis)):
                if self.__line & elem:
                    multiline.append(axes[idx])

        geom = shapely.MultiLineString(multiline).buffer(line_width / 2.0)
        if self.__corner:
            r = self.__corner * min(maxx, maxy)
            geom = geom.union(
                shapely.Polygon(
                    [
                        (minx + r, maxy),
                        (minx, maxy),
                        (minx, maxy - r),
                    ]
                )
            )
        return ShapelyGeometry(geom)


class OutlineGenerator(SilkscreenLineGenerator):
    __line_width: float | None = None

    def line_width(self, width: float):
        """Override the line width for this generator only. If not specified,
        the line width from the landpattern generator is used."""
        self.__line_width = width
        return self

    def _line_width(self, target: SilkscreenOutline) -> float:
        return self.__line_width or target._line_width

    def make_bounds(self, target: SilkscreenOutline) -> Bounds:
        """Generate the silkscreen outline"""
        raise NotImplementedError

    def make_shape(self, target: SilkscreenOutline) -> Shape:
        return self._silkscreen_line(self.make_bounds(target), self._line_width(target))


class SoldermaskBased(OutlineGenerator):
    @override
    def make_bounds(self, target: SilkscreenOutline) -> Bounds:
        line_width = self._line_width(target)
        clearance = target._silkscreen_soldermask_clearance

        sm_bounds = target._applies_to_bounds(Soldermask)
        margin = clearance + line_width / 2.0
        buffered_bounds = buffer_bounds(sm_bounds, margin)
        if bounds_area(buffered_bounds) <= 0.0:
            raise ValueError(
                "Soldermask bounds are too small to construct soldermask-based"
                + f" silkscreen outline: {sm_bounds}"
            )
        return buffered_bounds


class PackageBased(OutlineGenerator):
    @override
    def make_bounds(self, target: SilkscreenOutline) -> Bounds:
        pb = target._package_body()
        dl = target._density_level

        pb_bounds = pb.envelope(dl).to_shapely().bounds
        if bounds_area(pb_bounds) <= 0.0:
            raise ValueError(
                "Package body envelope is too small to construct package-based"
                + f" silkscreen outline: {pb_bounds}"
            )
        return pb_bounds


class SilkscreenOutline(
    ApplyToMixin,
    PackageBodyMixin,
    SilkscreenSoldermaskClearanceMixin,
    DensityLevelMixin,
    LineWidthMixin,
    LandpatternGenerator,
):
    """Silkscreen Outline"""

    outline: Silkscreen | None = None
    __generators: Sequence[OutlineGenerator] | None = (SoldermaskBased(),)
    __side: Side = Side.Top

    @overload
    def silkscreen_outline(self, generator: None) -> Self: ...
    @overload
    def silkscreen_outline(
        self,
        generator: OutlineGenerator,
        *fallback: OutlineGenerator,
        on: Side = Side.Top,
    ) -> Self: ...

    def silkscreen_outline(
        self,
        generator: OutlineGenerator | None,
        *fallback: OutlineGenerator,
        on: Side = Side.Top,
    ) -> Self:
        """Add a silkscreen outline to the landpattern.

        Args:
            generator: The outline generator to use. If None, the outline will be
                removed.
            fallback: Additional outline generators to try if the first one
                fails, e.g. if running out of space.
            on: The side of the board to apply the outline to.
        """
        if generator is None:
            self.__generators = None
        else:
            self.__generators = (generator,) + fallback
            self.__side = on
        return self

    @override
    def _build(self):
        self.outline = None
        super()._build()

    @override
    def _build_decorate(self):
        super()._build_decorate()
        if self.__generators:
            margin = self._silkscreen_soldermask_clearance
            masked = ShapelyGeometry(
                shapely.unary_union(
                    [sh.to_shapely().g for sh in self._applies_to_shapes(Soldermask)]
                )
            ).buffer(margin)

            generators = iter(self.__generators)
            gen = next(generators, None)
            while gen:
                try:
                    self.outline = Silkscreen(
                        gen.make_shape(self).to_shapely().difference(masked),
                        side=self.__side,
                    )
                    return
                except ValueError:
                    old_gen = gen
                    gen = next(generators, None)
                    if gen is None:
                        raise
                    logger.info(
                        f"Failed to construct silkscreen outline with {old_gen}, trying {gen}"
                    )


class InterstitialOutline(OutlineGenerator, SilkscreenSoldermaskClearanceMixin):
    """Interstitial Silkscreen Outline Generator

    This class constructs a rectangular outline surrounding the interstitial
    (interior) region of a landpattern. This typically corresponds to the area
    where the package body of the component rests. The interstitial region is
    estimated based on the inside edges of the pads, this works best for
    two-pin, dual-column, and quad-column packages.

    This outline style is commonly used for packages such as QFP, SOIC, SSOP.
    It is also commonly used for 2-pin SMT and through-hole components.

    >>> class MyComponent(Component):
    ...     landpattern = LandpatternWithOutline(
    ...     ).silkscreen_outline(InterstitialOutline())
    """

    @overload
    def __init__(self): ...
    @overload
    def __init__(self, *, vertical: bool): ...
    @overload
    def __init__(self, *, horizontal: bool): ...

    def __init__(self, *, vertical: bool = False, horizontal: bool = False):
        """
        Initialize the interstitial outline generator, optionally extending the
        outline to the vertical or horizontal bounds. This is useful for column
        packages such as SOIC, where the outline would otherwise stop short of
        the edge at the inside of the end pads.

        Args:
            vertical: If True, the outline will be extended to the vertical bounds.
            horizontal: If True, the outline will be horizontal to the horizontal bounds.
        """
        super().__init__()
        self.__vertical = vertical
        self.__horizontal = horizontal

    @override
    def make_bounds(self, target: SilkscreenOutline) -> Bounds:
        line_width = target._line_width
        clearance = self._silkscreen_soldermask_clearance

        inf = float("inf")
        hibounds = [inf, inf, -inf, -inf]
        lobounds = [inf, inf, -inf, -inf]
        for shape in target._applies_to_shapes(Soldermask):
            lox, loy, hix, hiy = shape.to_shapely().bounds
            hibounds[0] = min(hibounds[0], hix)
            hibounds[1] = min(hibounds[1], hiy)
            hibounds[2] = max(hibounds[2], hix)
            hibounds[3] = max(hibounds[3], hiy)
            lobounds[0] = min(lobounds[0], lox)
            lobounds[1] = min(lobounds[1], loy)
            lobounds[2] = max(lobounds[2], lox)
            lobounds[3] = max(lobounds[3], loy)

        margin = clearance + line_width / 2.0
        if self.__vertical:
            bounds = (hibounds[0], lobounds[1], lobounds[2], hibounds[3])
            adjust = -margin, 0
        elif self.__horizontal:
            bounds = (lobounds[0], hibounds[1], hibounds[2], lobounds[3])
            adjust = 0, -margin
        else:
            bounds = (hibounds[0], hibounds[1], lobounds[2], lobounds[3])
            adjust = -margin, -margin
        buffered_bounds = buffer_bounds(bounds, adjust)
        if bounds_area(buffered_bounds) <= 0.0:
            raise ValueError(
                "Soldermask bounds are too small to construct an interstitial"
                + f" soldermask-based silkscreen outline: {bounds}"
            )
        return buffered_bounds
