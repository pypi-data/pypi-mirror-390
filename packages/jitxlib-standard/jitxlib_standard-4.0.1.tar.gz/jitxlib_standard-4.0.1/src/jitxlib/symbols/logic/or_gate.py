"""
OR gate symbol for JITX Standard Library
"""

from __future__ import annotations
import math
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, cast

from jitx.shapes import Shape
from jitx.shapes.primitive import Arc, ArcPolygon, ArcPolyline, Polyline
from jitx.symbol import Direction, Pin

from ..common import (
    DEF_FILLED,
    DEF_LINE_WIDTH,
    DEF_PIN_LENGTH,
    DEF_PAD_NAME_SIZE,
)
from ..decorators import (
    ActiveLow,
    OpenCollector,
    OpenCollectorType,
    draw,
)
from ..label import LabelConfigurable, LabelledSymbol

if TYPE_CHECKING:
    from ..context import SymbolStyleContext


# OR gate symbol geometry ratios based on IEEE standard
DEF_OR_APEX_TO_CENTERS_RATIO = 10.0 / 26.0
DEF_OR_REAR_CURVE_R_TO_H_RATIO = 26.0 / 26.0
DEF_OR_XOR_CURVE_R_TO_H_RATIO = 26.0 / 26.0
DEF_OR_XOR_OFFSET_TO_H_RATIO = 5.0 / 26.0

DEF_OR_HEIGHT = 3.0
DEF_OR_NUM_INPUTS = 2
DEF_OR_PIN_PITCH = 2


@dataclass
class ORGateConfig(LabelConfigurable):
    """
    Configuration for OR gate symbols

    Defines the geometric and visual parameters for OR gate symbols.
    """

    height: float = DEF_OR_HEIGHT
    """Gate body height"""
    filled: bool = DEF_FILLED
    """Whether to fill the gate body"""
    line_width: float = DEF_LINE_WIDTH
    """Width of the gate lines"""
    pin_length: int = DEF_PIN_LENGTH
    """Length of the pin extensions"""
    pad_name_size: float | None = DEF_PAD_NAME_SIZE
    """Size of the pad name text"""
    num_inputs: int = DEF_OR_NUM_INPUTS
    """Number of input pins"""
    pin_pitch: int = DEF_OR_PIN_PITCH
    """Spacing between input pins"""
    inverted: bool = False
    """Whether to add inversion bubble (creates NOR gate)"""
    exclusive: bool = False
    """Whether to make XOR/XNOR gate (adds extra input arc)"""
    open_collector: OpenCollectorType | None = None
    """Whether to add open-collector symbol on output pin"""

    def __post_init__(self):
        if self.pin_length < 0:
            raise ValueError("OR gate pin_length must be non-negative")
        if self.pad_name_size is not None and self.pad_name_size < 0:
            raise ValueError("OR gate pad_name_size must be non-negative")
        if self.num_inputs < 2:
            raise ValueError("OR gate must have at least 2 inputs")
        if self.pin_pitch < 1:
            raise ValueError("OR gate pin_pitch must be at least 1")


class ORGateSymbol[T: ORGateConfig](LabelledSymbol):
    """
    OR gate symbol with graphics and pins.
    Supports XOR, NOR, and XNOR functionality.
    """

    config: T
    gate_body: Shape[ArcPolyline | ArcPolygon]
    xor_arc: Shape[ArcPolyline] | None = None
    leader_pins: tuple[Shape[Polyline], ...]
    p: dict[int, Pin]

    def _symbol_style_config(self, context: SymbolStyleContext | None = None) -> T:
        """Symbol style config for this OR gate symbol."""
        if context is None:
            config = ORGateConfig()
        else:
            config = context.or_gate_config
        # Casting necessary because ORGateSymbol is both a generic and a concrete class.
        return cast(T, config)

    def _lookup_config(
        self, config: T | None = None, context: SymbolStyleContext | None = None
    ) -> T:
        """Lookup the config for this symbol."""

        if config is None:
            return self._symbol_style_config(context)
        return config

    def __init__(self, config: T | None = None, **kwargs):
        """
        Initialize OR gate symbol

        Args:
            config: Config object, or None to use defaults
            **kwargs: Individual parameters to override defaults
        """

        # Apparently this needs to be imported here, even though SymbolStyleContext is imported in TYPE_CHECKING.
        from ..context import SymbolStyleContext

        context = SymbolStyleContext.get()
        config = self._lookup_config(config, context)
        self.config = replace(config, **kwargs)

        # Validate inputs
        if self.config.num_inputs < 2:
            raise ValueError("OR gate must have at least 2 inputs")

        self._build_gate_body()
        self._build_pins()
        self._build_labels(ref=Direction.Up, value=Direction.Up)

        self.pad_name_size = self.config.pad_name_size

    def _compute_centers_to_origin(self, h: float) -> float:
        """Compute the centers offset from the origin using Pythagorean theorem."""
        c = h
        a = h / 2.0
        return math.sqrt(c**2 - a**2)

    def _compute_rear_arc_radius(self, h: float) -> float:
        """Compute the radius for the rear arc."""
        return DEF_OR_REAR_CURVE_R_TO_H_RATIO * h

    def _compute_rear_arc_center(self, h: float) -> tuple[float, float]:
        """Compute the center point for the rear arc."""
        centers_to_origin = self._compute_centers_to_origin(h)
        rear_apex_to_centers = DEF_OR_APEX_TO_CENTERS_RATIO * h
        rear_r = self._compute_rear_arc_radius(h)
        x_off = centers_to_origin + rear_apex_to_centers + rear_r
        return (-x_off, 0.0)

    def _compute_rear_arc_end_point(self, h: float) -> tuple[float, float]:
        """Compute the end point for the rear arc."""
        rear_r = self._compute_rear_arc_radius(h)
        rear_center = self._compute_rear_arc_center(h)

        # Use Pythagorean theorem to compute the X offset of the rear arc endpoint
        c = rear_r
        a = h / 2.0
        b = math.sqrt(c**2 - a**2)

        x_off = rear_center[0] + b
        return (x_off, a)

    def _compute_rear_arc_sweep(self, h: float) -> float:
        """Compute rear arc sweep angle in degrees."""
        rear_center = self._compute_rear_arc_center(h)
        rear_ep = self._compute_rear_arc_end_point(h)

        xy_x = rear_ep[0] - rear_center[0]
        xy_y = rear_ep[1] - rear_center[1]
        return math.degrees(2.0 * math.atan(xy_y / xy_x))

    def _compute_front_arc_sweep(self, h: float) -> float:
        """Compute the front arc sweep angle in degrees."""
        x_off = self._compute_centers_to_origin(h)
        return math.degrees(math.atan(x_off / (h / 2.0)))

    def _compute_symbol_width(self, h: float, exclusive: bool) -> float:
        """Compute the symbol width."""
        rear_ep = self._compute_rear_arc_end_point(h)
        xor_offset = DEF_OR_XOR_OFFSET_TO_H_RATIO * h if exclusive else 0.0
        return abs(rear_ep[0]) + xor_offset

    def _get_input_pin_positions(self, width: float) -> list[tuple[int, int]]:
        """Compute the input pin positions."""
        num_pins = self.config.num_inputs
        pin_pitch = self.config.pin_pitch
        y_start = math.floor((num_pins - 1) * pin_pitch / 2)
        width = math.ceil(width)
        return [(-width, math.ceil(y_start - (i * pin_pitch))) for i in range(num_pins)]

    def _build_gate_body(self) -> None:
        """Build the OR gate body shape."""
        h = self.config.height
        h2 = h / 2.0

        ctr_offset = self._compute_centers_to_origin(h)
        front_r = h
        front_sweep = self._compute_front_arc_sweep(h)
        top_front_start = 90.0 - front_sweep

        # Front arcs (curved input side)
        top_front_arc = Arc((-ctr_offset, -h2), front_r, top_front_start, front_sweep)
        bot_front_arc = Arc((-ctr_offset, h2), front_r, 270.0, front_sweep)

        # Rear arc geometry
        top_rear_ep = self._compute_rear_arc_end_point(h)
        bot_rear_ep = (top_rear_ep[0], -top_rear_ep[1])

        rear_center = self._compute_rear_arc_center(h)
        rear_sweep = self._compute_rear_arc_sweep(h)
        rear_arc = Arc(
            rear_center,
            h,  # rear radius = h
            rear_sweep / 2.0,
            -rear_sweep,
        )

        # Build the main body
        body_points = [
            top_front_arc,
            (-ctr_offset, h2),
            top_rear_ep,
            rear_arc,
            bot_rear_ep,
            (-ctr_offset, -h2),
            bot_front_arc,
            (0.0, 0.0),  # Output point
        ]

        if self.config.filled:
            self.gate_body = ArcPolygon(body_points)
        else:
            self.gate_body = ArcPolyline(self.config.line_width, body_points)

        if not self.config.exclusive:
            arc_center = rear_center
            arc_r = h
        else:
            xor_r = DEF_OR_XOR_CURVE_R_TO_H_RATIO * h
            xor_offset_x = DEF_OR_XOR_OFFSET_TO_H_RATIO * h
            xor_center = (rear_center[0] - xor_offset_x, rear_center[1])
            top_xor_ep = (top_rear_ep[0] - xor_offset_x, top_rear_ep[1])
            bot_xor_ep = (bot_rear_ep[0] - xor_offset_x, bot_rear_ep[1])

            xor_arc = Arc(
                xor_center,
                xor_r,
                rear_sweep / 2.0,
                -rear_sweep,
            )
            self.xor_arc = ArcPolyline(
                self.config.line_width,
                [
                    top_xor_ep,
                    xor_arc,
                    bot_xor_ep,
                ],
            )
            arc_center = xor_center
            arc_r = xor_r

        w = self._compute_symbol_width(h, self.config.exclusive)
        input_pin_positions = self._get_input_pin_positions(w)
        eps = 0.01
        leader_pins = []

        for pin_pos in input_pin_positions:
            b = math.sqrt(arc_r**2 - pin_pos[1] ** 2)
            arc_x = arc_center[0] + b
            leader_pos = (arc_x, pin_pos[1])
            leader_len = abs(pin_pos[0] - arc_x)
            if leader_len > eps:
                leader_pins.append(
                    Polyline(self.config.line_width, [pin_pos, leader_pos])
                )

        self.leader_pins = tuple(leader_pins)

    def _build_pins(self) -> None:
        """Build input and output pins for the OR gate."""
        w = self._compute_symbol_width(self.config.height, self.config.exclusive)
        input_pin_positions = self._get_input_pin_positions(w)
        self.p = {
            i + 1: Pin(
                at=pin_pos, direction=Direction.Left, length=self.config.pin_length
            )
            for i, pin_pos in enumerate(input_pin_positions)
        }

        out_pos = (0, 0)
        out_dir = Direction.Right
        self.p[self.config.num_inputs + 1] = Pin(
            at=out_pos, direction=out_dir, length=self.config.pin_length
        )

        self.pin_decorators = []
        if self.config.inverted:
            self.pin_decorators.append(draw(ActiveLow(), out_dir, out_pos))

        if self.config.open_collector is not None:
            self.pin_decorators.append(
                draw(
                    OpenCollector(oc_type=self.config.open_collector),
                    out_dir,
                    out_pos,
                )
            )

    # Convenience properties to access config values
    @property
    def height(self) -> float:
        """See :attr:`~.ORGateConfig.height`."""
        return self.config.height

    @property
    def filled(self) -> bool:
        """See :attr:`~.ORGateConfig.filled`."""
        return self.config.filled

    @property
    def line_width(self) -> float:
        """See :attr:`~.ORGateConfig.line_width`."""
        return self.config.line_width

    @property
    def pin_length(self) -> float:
        """See :attr:`~.ORGateConfig.pin_length`."""
        return self.config.pin_length

    @property
    def num_inputs(self) -> int:
        """See :attr:`~.ORGateConfig.num_inputs`."""
        return self.config.num_inputs

    @property
    def pin_pitch(self) -> float:
        """See :attr:`~.ORGateConfig.pin_pitch`."""
        return self.config.pin_pitch

    @property
    def inverted(self) -> bool:
        """See :attr:`~.ORGateConfig.inverted`."""
        return self.config.inverted

    @property
    def exclusive(self) -> bool:
        """See :attr:`~.ORGateConfig.exclusive`."""
        return self.config.exclusive

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config
