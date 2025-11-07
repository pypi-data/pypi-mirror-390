from __future__ import annotations
from typing import override

from jitx.feature import Soldermask, KeepOut
from jitx.layerindex import LayerSet
from jitx.shapes.composites import (
    Bounds,
    bounds_area,
    buffer_bounds,
    rectangle_from_bounds,
)

from . import ApplyToMixin, LandpatternGenerator, LandpatternProvider


DEF_KEEPOUT_LAYERS = LayerSet(0)
INFINITY = float("inf")


class KeepoutGenerator:
    def make_keepout(self, target: KeepoutGeneratorMixin) -> KeepOut:
        raise NotImplementedError(f"{self.__class__.__name__}.make_keepout")


class KeepoutGeneratorMixin(
    ApplyToMixin,
    LandpatternProvider,
):
    __generator: KeepoutGenerator | None = None
    _keepout: KeepOut | None = None

    def keepout(self, generator: KeepoutGenerator):
        """Add a keepout generator to the landpattern"""
        self.__generator = generator
        return self

    @override
    def _build(self):
        # wipe any existing courtyard to prevent re-discovery on subsequent runs
        self._keepout = None
        super()._build()

    @override
    def _build_decorate(self):
        super()._build_decorate()
        if self.__generator is not None:
            self._keepout = self.__generator.make_keepout(self)


class IntraKeepoutGenerator(KeepoutGenerator):
    """Intra-Package Keepout Generator

    This class generates a rectangular keepout which fills the interstitial
    region between the pads of a landpattern.
    """

    def __init__(
        self,
        *,
        vertical: bool = False,
        horizontal: bool = False,
        layers: LayerSet | None = None,
        keepout_adj: float | tuple[float, float] | None = None,
    ):
        """Intra-package Keepout Generator

        Initializes a keepout feature in the interstitial region between the
        interior bounds of the pads of a landpattern. This is defined as the
        region between the lowest upper bound and the highest lower bound of any
        pad along each dimension. Optionally, the keepout can be extended to the
        full bounds in either dimension (i.e. lowest lower bound to highest
        upper bound of any pad) using the ``vertical`` and ``horizontal`` flags.
        This is useful for packages such as SOICs, where the interstitial region
        would otherwise stop short of the edge at the inside of the end pads.

        Args:
            vertical: If True, the keepout will be extended to the vertical
                bounds.
            horizontal: If True, the keepout will be extended to the horizontal
                bounds.
            layers: optional, layers to use for the keepout. If unspecified,
                the default is to only generate on the top layer.
            keepout_adj: optional, amount to buffer the interstital region by
                to generate the keepout. If this is a tuple, the first element
                is the horizontal buffer and the second element is the vertical
                buffer. This is usually a negative value. If unspecified, the
                default value is 0.0. This does not affect dimensions which are
                extended to the full bounds (i.e. the height if ``vertical`` is
                True, or the width if ``horizontal`` is True).
        """

        self.__vertical = vertical
        self.__horizontal = horizontal
        self.__layers = layers
        self.__keepout_adj = keepout_adj

    def make_keepout(self, target: KeepoutGeneratorMixin) -> KeepOut:
        match self.__keepout_adj:
            case float():
                adj_x = self.__keepout_adj
                adj_y = self.__keepout_adj
            case tuple():
                adj_x, adj_y = self.__keepout_adj
            case _:
                adj_x = 0.0
                adj_y = 0.0

        # ``rearrange_fn`` swaps, for each axis, the upper and lower extents of
        # the pad shape along that axis. Unioning these rearranged extents
        # gives the bounds of the interstitial region (minimum upper extent to
        # maximum lower extent).
        # However, if the keepout is extended to the full extent in one or more
        # axes by using the ``vertical`` or ``horizontal`` flags, the bounds for
        # those axes should be left unswapped instead. This match statement sets
        # the correct ``rearrange_fn`` for each case.
        # Also, the adjustment is set to 0.0 for axes which are fully-extended
        match self.__vertical, self.__horizontal:
            case True, True:
                rearrange_fn = no_transpose
                adj_x = 0.0
                adj_y = 0.0
            case True, False:
                rearrange_fn = transpose_x
                adj_y = 0.0
            case False, True:
                rearrange_fn = transpose_y
                adj_x = 0.0
            case _:
                rearrange_fn = transpose_bounds

        bounds = (INFINITY, INFINITY, -INFINITY, -INFINITY)
        for shape in target._applies_to_shapes(Soldermask):
            shape_bounds = shape.to_shapely().bounds
            re_bounds = rearrange_fn(shape_bounds)
            bounds = bounds_union(bounds, re_bounds)

        if bounds_area(bounds) <= 0.0:
            raise ValueError("Interstitial keepout bounds are empty")
        bounds = buffer_bounds(bounds, (adj_x, adj_y))
        if bounds_area(bounds) <= 0.0:
            raise ValueError("Not enough space to construct interstitial keepout")
        keepout_shape = rectangle_from_bounds(bounds)
        if self.__layers is None:
            layers = DEF_KEEPOUT_LAYERS
        else:
            layers = self.__layers
        return KeepOut(keepout_shape, layers=layers, pour=True)


class IntraKeepout(KeepoutGeneratorMixin, LandpatternGenerator):
    """A keepout generator mixin with default IntraKeepout generator."""

    @override
    def __base_init__(self):
        super().__base_init__()
        self.keepout(IntraKeepoutGenerator())


def bounds_union(b1: Bounds, b2: Bounds) -> Bounds:
    return (
        min(b1[0], b2[0]),
        min(b1[1], b2[1]),
        max(b1[2], b2[2]),
        max(b1[3], b2[3]),
    )


def transpose_bounds(b: Bounds) -> Bounds:
    """Flips the min/max sides of a bounds"""
    return (b[2], b[3], b[0], b[1])


def transpose_x(b: Bounds) -> Bounds:
    """Flips the min/max x values of a bounds"""
    return (b[2], b[1], b[0], b[3])


def transpose_y(b: Bounds) -> Bounds:
    """Flips the min/max y values of a bounds"""
    return (b[0], b[3], b[2], b[1])


def no_transpose(b: Bounds) -> Bounds:
    """No-op transpose function"""
    return b
