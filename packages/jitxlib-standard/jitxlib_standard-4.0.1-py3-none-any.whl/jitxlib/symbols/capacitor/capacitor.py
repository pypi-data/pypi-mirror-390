"""
Capacitor symbol for JITX Standard Library
"""

from __future__ import annotations
import math
from enum import Enum
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, cast, override

from jitx.shapes import Shape
from jitx.shapes.primitive import Arc, ArcPolyline, Polyline
from jitx.symbol import Direction, Pin

from jitx.transform import Transform
from jitx.units import percent, Quantity
from ..common import DEF_LINE_WIDTH
from ..label import LabelConfigurable, LabelledSymbol

if TYPE_CHECKING:
    from ..context import SymbolStyleContext


def _resolve_value(value: float, reference: float) -> float:
    """Resolve a value that could be absolute or percentage"""
    if isinstance(value, Quantity):
        if str(value.units) == "percent":
            # Convert percentage to absolute
            return value.magnitude * reference / 100.0
        else:
            # Other units - just use magnitude
            return float(value.magnitude)
    else:
        # Plain float/int - use as absolute
        return float(value)


class PolarizedStyle(Enum):
    """
    Polarized capacitor symbol styles

    Defines the visual representation style for polarized capacitor symbols.
    """

    STRAIGHT = "straight"
    CURVED = "curved"


# CapacitorConfig constants
DEF_CAP_PITCH = 4.0
DEF_CAP_PORCH_WIDTH = 80 * percent  # 80% of pitch/2
DEF_CAP_WIDTH = 3.0
DEF_CAP_POL_STYLE = PolarizedStyle.STRAIGHT
DEF_CAP_POL_RADIUS = 5.0
DEF_CAP_PLUS_SIZE = 20 * percent  # 20% of width


@dataclass
class CapacitorConfig(LabelConfigurable):
    """
    Configuration for capacitor symbols

    Defines the geometric and visual parameters for capacitor symbols.
    """

    pitch: float = DEF_CAP_PITCH
    """Distance between pin points"""
    width: float = DEF_CAP_WIDTH
    """Width of the capacitor plates"""
    porch_width: float = DEF_CAP_PORCH_WIDTH
    """Length of line from pin to capacitor plate (absolute or percentage of pitch/2)"""
    line_width: float = DEF_LINE_WIDTH
    """Width of the capacitor lines"""


class CapacitorSymbol[T: CapacitorConfig](LabelledSymbol):
    """
    Capacitor symbol with graphics and pins.
    Also serves as the base class for all other capacitor symbol types.
    """

    config: T
    capacitor_top_plate: tuple[Shape[Polyline], Shape[Polyline]]  # (porch, plate)
    capacitor_bottom_plate: tuple[
        Shape[Polyline], Shape[Polyline] | Shape[ArcPolyline]
    ]  # (porch, plate)

    def _symbol_style_config(self, context: SymbolStyleContext | None = None) -> T:
        """Symbol style config for this capacitor symbol."""
        if context is None:
            config = CapacitorConfig()
        else:
            config = context.capacitor_config
        # Casting necessary because CapacitorSymbol is both a generic and a concrete class.
        return cast(T, config)

    def _lookup_config(
        self, config: T | None = None, context: SymbolStyleContext | None = None
    ) -> T:
        """Lookup the config for this symbol."""

        if config is None:
            return self._symbol_style_config(context)
        return config

    # TODO: Look into making kwargs type-specific using a paramspec (same for resistor class).
    def __init__(self, config: T | None = None, **kwargs):
        """
        Initialize capacitor symbol

        Args:
            config: Config object, or None to use defaults
            **kwargs: Individual parameters to override defaults
        """

        # Apparently this needs to be imported here, even though SymbolStyleContext is imported in TYPE_CHECKING.
        from ..context import SymbolStyleContext

        context = SymbolStyleContext.get()
        config = self._lookup_config(config, context)
        self.config = replace(config, **kwargs)

        self._build_capacitor_plates()
        self._build_pins()
        self._build_labels(ref=Direction.Right, value=Direction.Right)

    def _build_pins(self) -> None:
        """Build 'p[1]' and 'p[2]' symbol pins for the capacitor."""
        # Floor keeps the pins on the grid.
        w = math.floor(self.pitch / 2)
        self.p = {
            1: Pin(at=(0, w), direction=Direction.Up),
            2: Pin(at=(0, -w), direction=Direction.Down),
        }

    def _top_plate(
        self, width: float, top: float, cross_y: float, line_width: float
    ) -> tuple[Shape[Polyline], Shape[Polyline]]:
        """Construct the capacitor porch and plate shapes that make up the top plate."""
        w2 = width / 2.0
        porch = Polyline(
            line_width,
            [(0.0, top), (0.0, cross_y)],
        )
        plate = Polyline(
            line_width,
            [
                (-w2, cross_y),
                (w2, cross_y),
            ],
        )
        return (porch, plate)

    def _build_capacitor_plates(self) -> None:
        """Build the capacitor plates (top and bottom)."""
        h = self.pitch / 2.0

        # Resolve porch_width (could be absolute or percentage of pitch/2)
        actual_porch_width = _resolve_value(self.porch_width, h)

        # Y point at which the cross bar for the capacitor plate starts
        cross_y = h - actual_porch_width

        # Build top plate
        porch, plate = self._top_plate(self.width, h, cross_y, self.line_width)
        self.capacitor_top_plate = (porch, plate)

        # Build bottom plate (rotated 180 degrees)
        rotate = Transform((0, 0), 180)
        self.capacitor_bottom_plate = (rotate * porch, rotate * plate)

    # Convenience properties to access config values
    @property
    def pitch(self) -> float:
        """See :attr:`~.CapacitorConfig.pitch`."""
        return self.config.pitch

    @property
    def porch_width(self) -> float:
        """See :attr:`~.CapacitorConfig.porch_width`."""
        return self.config.porch_width

    @property
    def width(self) -> float:
        """See :attr:`~.CapacitorConfig.width`."""
        return self.config.width

    @property
    def line_width(self) -> float:
        """See :attr:`~.CapacitorConfig.line_width`."""
        return self.config.line_width

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config


@dataclass
class PolarizedCapacitorConfig(CapacitorConfig):
    """
    Configuration for polarized capacitor symbols

    Extends CapacitorConfig with polarized-specific parameters.
    """

    style: PolarizedStyle = DEF_CAP_POL_STYLE
    """Visual style for the polarized capacitor (straight or curved)"""
    pol_radius: float = DEF_CAP_POL_RADIUS
    """Radius for the curved bottom plate in curved style"""
    plus_size: float = DEF_CAP_PLUS_SIZE
    """Size of the plus sign indicator (absolute or percentage of width)"""


class PolarizedCapacitorSymbol[T: PolarizedCapacitorConfig](CapacitorSymbol):
    """
    Polarized capacitor symbol with graphics and pins.
    Supports both straight and curved bottom plate styles.
    """

    config: T
    plus_sign: tuple[Shape[Polyline], Shape[Polyline]] | None = None
    a: Pin
    c: Pin

    @override
    def _symbol_style_config(
        self, context: SymbolStyleContext | None = None
    ) -> PolarizedCapacitorConfig:
        """Symbol style config for this polarized capacitor symbol."""
        if context is None:
            return PolarizedCapacitorConfig()
        else:
            return context.polarized_capacitor_config

    @override
    def _build_pins(self) -> None:
        """Build 'a' and 'c' symbol pins for the capacitor."""
        # Floor keeps the pins on the grid.
        w = math.floor(self.pitch / 2)
        self.a = Pin(at=(0, w), direction=Direction.Up)
        self.c = Pin(at=(0, -w), direction=Direction.Down)

    @override
    def _build_capacitor_plates(self) -> None:
        """Build the capacitor plates (top and bottom) with polarized styling."""
        h = self.pitch / 2.0

        # Resolve porch_width (could be absolute or percentage of pitch/2)
        actual_porch_width = _resolve_value(self.porch_width, h)

        # Y point at which the cross bar for the capacitor plate starts
        cross_y = h - actual_porch_width

        # Build plus sign
        self._build_plus_sign(cross_y)

        if self.config.style == PolarizedStyle.STRAIGHT:
            # Straight style - same as regular capacitor
            super()._build_capacitor_plates()
            return

        elif self.config.style == PolarizedStyle.CURVED:
            self.capacitor_top_plate = self._top_plate(
                self.width, h, cross_y, self.line_width
            )
            # Curved style - use arc for bottom plate
            self.capacitor_bottom_plate = self._curved_bottom_plate(h, cross_y)

    def _curved_bottom_plate(
        self, h: float, cross_y: float
    ) -> tuple[Shape[Polyline], ArcPolyline]:
        """Construct the porch and curved plate that make up the bottom plate."""
        pol_r = self.config.pol_radius
        w2 = self.width / 2.0
        half_angle = math.degrees(math.atan(w2 / pol_r))

        # Porch line
        porch_line = Polyline(self.line_width, [(0.0, -h), (0.0, -cross_y)])

        # Create the arc (curved part of the bottom plate)
        arc_center = (0.0, -(cross_y + pol_r))
        arc_polyline = ArcPolyline(
            self.line_width,
            [
                Arc(arc_center, pol_r, 90.0 - half_angle, 2 * half_angle),
            ],
        )

        return (porch_line, arc_polyline)

    def _build_plus_sign(self, cross_y: float) -> None:
        """Build the plus sign indicator for the polarized capacitor."""
        # Resolve plus_size (could be absolute or percentage of width)
        plus_len = _resolve_value(self.config.plus_size, self.width)

        arm = plus_len / 2.0
        x_pos = (self.width / 2.0) - arm
        y_pos = cross_y + (2.0 * arm)

        plus_line1 = Polyline(self.line_width, [(-arm, 0.0), (arm, 0.0)])
        plus_line2 = Polyline(self.line_width, [(0.0, -arm), (0.0, arm)])
        transform = Transform((x_pos, y_pos))
        self.plus_sign = (transform * plus_line1, transform * plus_line2)

    # Additional convenience properties for polarized capacitor
    @property
    def style(self) -> PolarizedStyle:
        """See :attr:`~.PolarizedCapacitorConfig.style`."""
        return self.config.style

    @property
    def pol_radius(self) -> float:
        """See :attr:`~.PolarizedCapacitorConfig.pol_radius`."""
        return self.config.pol_radius

    @property
    def plus_size(self) -> float:
        """See :attr:`~.PolarizedCapacitorConfig.plus_size`."""
        return self.config.plus_size
