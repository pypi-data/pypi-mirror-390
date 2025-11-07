"""
AND gate symbol for JITX Standard Library
"""

from __future__ import annotations
import math
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, cast

from jitx import UserCodeException
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


# IEEE sets the AND gate symbol w/h ratio to 32.0 / 26.0 = 1.231
DEF_AND_W_OVER_H_RATIO = 32.0 / 26.0
DEF_AND_HEIGHT = 4.0
DEF_AND_NUM_INPUTS = 2
DEF_AND_PIN_PITCH = 2


@dataclass
class ANDGateConfig(LabelConfigurable):
    """
    Configuration for AND gate symbols

    Defines the geometric and visual parameters for AND gate symbols.
    """

    height: float = DEF_AND_HEIGHT
    """Gate body height"""
    width: float | None = None
    """Gate body width (from input edge to output tip). If None, automatically computed as height * width_to_height_ratio"""
    width_to_height_ratio: float = DEF_AND_W_OVER_H_RATIO
    """Width to height ratio for automatic width calculation"""
    filled: bool = DEF_FILLED
    """Whether to fill the gate body"""
    line_width: float = DEF_LINE_WIDTH
    """Width of the gate lines"""
    pin_length: int = DEF_PIN_LENGTH
    """Length of the pin extensions"""
    pad_name_size: float | None = DEF_PAD_NAME_SIZE
    """Size of the pad name text"""
    num_inputs: int = DEF_AND_NUM_INPUTS
    """Number of input pins"""
    pin_pitch: int = DEF_AND_PIN_PITCH
    """Spacing between input pins"""
    inverted: bool = False
    """Whether to add inversion bubble (creates NAND gate)"""
    open_collector: OpenCollectorType | None = None
    """Whether to add open-collector symbol on output pin"""

    def get_effective_width(self) -> float:
        """Get the effective width, computing it from height and ratio if not explicitly set"""
        if self.width is not None:
            return self.width
        return self.height * self.width_to_height_ratio

    def __post_init__(self):
        if self.pin_length < 0:
            raise ValueError("AND gate pin_length must be non-negative")
        if self.pad_name_size is not None and self.pad_name_size < 0:
            raise ValueError("AND gate pad_name_size must be non-negative")
        if self.num_inputs < 2:
            raise ValueError("AND gate must have at least 2 inputs")
        if self.pin_pitch < 1:
            raise ValueError("AND gate pin_pitch must be at least 1")


class ANDGateSymbol[T: ANDGateConfig](LabelledSymbol):
    """
    AND gate symbol with graphics and pins.
    Supports configurable number of inputs and NAND functionality.
    """

    config: T
    gate_body: Shape[ArcPolyline | ArcPolygon]
    leader_pins: tuple[Shape[Polyline], ...]
    p: dict[int, Pin]

    def _symbol_style_config(self, context: SymbolStyleContext | None = None) -> T:
        """Symbol style config for this AND gate symbol."""
        if context is None:
            config = ANDGateConfig()
        else:
            config = context.and_gate_config
        # Casting necessary because ANDGateSymbol is both a generic and a concrete class.
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
        Initialize AND gate symbol

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
            raise ValueError("AND gate must have at least 2 inputs")

        # Check if pin spacing exceeds available height
        required_height = self.config.pin_pitch * (self.config.num_inputs - 1)
        if required_height > self.config.height:
            raise UserCodeException(
                f"AND gate pin spacing ({required_height}) exceeds available height ({self.config.height}).\n"
                f"Minimum height required: pin_pitch * (num_inputs - 1) = {self.config.pin_pitch} * ({self.config.num_inputs} - 1) = {required_height}\n",
                f"Reduce pin_pitch ({self.config.pin_pitch}) or increase height ({self.config.height})",
            )

        self._build_gate_body()
        self._build_pins()
        self._build_labels(ref=Direction.Up, value=Direction.Up)

        self.pad_name_size = self.config.pad_name_size

    def _get_input_pin_positions(self) -> list[tuple[int, int]]:
        num_pins = self.config.num_inputs
        pin_pitch = self.config.pin_pitch
        y_start = math.floor((num_pins - 1) * pin_pitch / 2)
        width = math.ceil(self.config.get_effective_width())
        return [(-width, math.ceil(y_start - (i * pin_pitch))) for i in range(num_pins)]

    def _build_gate_body(self) -> None:
        """Build the AND gate body shape."""
        h = self.config.height
        w = self.config.get_effective_width()
        h2 = h / 2.0
        dome_r = h2

        # Add arc for the dome (right semicircle)
        arc_center = (-dome_r, 0.0)
        arc = Arc(arc_center, dome_r, 270.0, 180.0)

        # Complete the rectangle
        body_points = [
            (-h2, h2),  # Top left of rectangle
            (-w, h2),  # Top left corner
            (-w, -h2),  # Bottom left corner
            (-h2, -h2),  # Bottom left of rectangle
            arc,  # Right semicircle
        ]

        if self.config.filled:
            self.gate_body = ArcPolygon(body_points)
        else:
            self.gate_body = ArcPolyline(self.config.line_width, body_points)

        input_pin_positions = self._get_input_pin_positions()
        x_offset = input_pin_positions[0][0]
        diff = abs(w - abs(x_offset))
        eps = 0.01
        # If pin position offset is greater than epsilon
        #   then we want to draw leader pins for each of the pins.
        leader_pins = []
        if diff > eps:
            for pin_pos in input_pin_positions:
                line = Polyline(self.config.line_width, [pin_pos, (-w, pin_pos[1])])
                leader_pins.append(line)

        self.leader_pins = tuple(leader_pins)

    def _build_pins(self) -> None:
        """Build input and output pins for the AND gate."""
        input_pin_positions = self._get_input_pin_positions()
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
        """See :attr:`~.ANDGateConfig.height`."""
        return self.config.height

    @property
    def width(self) -> float:
        """See :attr:`~.ANDGateConfig.width`."""
        return self.config.get_effective_width()

    @property
    def filled(self) -> bool:
        """See :attr:`~.ANDGateConfig.filled`."""
        return self.config.filled

    @property
    def line_width(self) -> float:
        """See :attr:`~.ANDGateConfig.line_width`."""
        return self.config.line_width

    @property
    def pin_length(self) -> float:
        """See :attr:`~.ANDGateConfig.pin_length`."""
        return self.config.pin_length

    @property
    def num_inputs(self) -> int:
        """See :attr:`~.ANDGateConfig.num_inputs`."""
        return self.config.num_inputs

    @property
    def pin_pitch(self) -> float:
        """See :attr:`~.ANDGateConfig.pin_pitch`."""
        return self.config.pin_pitch

    @property
    def inverted(self) -> bool:
        """See :attr:`~.ANDGateConfig.inverted`."""
        return self.config.inverted

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config
