"""
Buffer/Inverter symbol for JITX Standard Library
"""

from __future__ import annotations
from dataclasses import dataclass, replace
import math
from typing import TYPE_CHECKING, cast

from jitx.shapes import Shape
from jitx.shapes.primitive import Polygon, Polyline
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


DEF_BUFFER_TRI_HEIGHT = 3.0
DEF_BUFFER_TRI_WIDTH = 2.0


@dataclass
class BufferConfig(LabelConfigurable):
    """
    Configuration for buffer/inverter symbols

    Defines the geometric and visual parameters for buffer symbols.
    """

    tri_height: float = DEF_BUFFER_TRI_HEIGHT
    """Triangle height (vertical dimension)"""
    tri_width: float = DEF_BUFFER_TRI_WIDTH
    """Triangle width (horizontal dimension)"""
    filled: bool = DEF_FILLED
    """Whether to fill the triangle body"""
    line_width: float = DEF_LINE_WIDTH
    """Width of the triangle lines"""
    pin_length: int = DEF_PIN_LENGTH
    """Length of the pin extensions"""
    pad_name_size: float | None = DEF_PAD_NAME_SIZE
    """Size of the pad name text"""
    inverter: bool = False
    """Whether to add inversion bubble (creates inverter)"""
    open_collector: OpenCollectorType | None = None
    """Whether to add open-collector symbol on output pin"""

    def __post_init__(self):
        if self.tri_height <= 0:
            raise ValueError("Buffer tri_height must be positive")
        if self.tri_width <= 0:
            raise ValueError("Buffer tri_width must be positive")
        if self.pin_length < 0:
            raise ValueError("Buffer pin_length must be non-negative")
        if self.pad_name_size is not None and self.pad_name_size < 0:
            raise ValueError("Buffer pad_name_size must be non-negative")


class BufferSymbol[T: BufferConfig](LabelledSymbol):
    """
    Buffer symbol with graphics and pins.
    Can be configured as buffer or inverter.
    """

    config: T
    triangle_body: Shape[Polyline] | Shape[Polygon]
    p: dict[int, Pin]

    def _symbol_style_config(self, context: SymbolStyleContext | None = None) -> T:
        """Symbol style config for this buffer symbol."""
        if context is None:
            config = BufferConfig()
        else:
            config = context.buffer_config
        # Casting necessary because BufferSymbol is both a generic and a concrete class.
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
        Initialize buffer symbol

        Args:
            config: Config object, or None to use defaults
            **kwargs: Individual parameters to override defaults
        """

        # Apparently this needs to be imported here, even though SymbolStyleContext is imported in TYPE_CHECKING.
        from ..context import SymbolStyleContext

        context = SymbolStyleContext.get()
        config = self._lookup_config(config, context)
        self.config = replace(config, **kwargs)

        self._build_triangle_body()
        self._build_pins()
        self._build_labels(ref=Direction.Up, value=Direction.Up)

        self.pad_name_size = self.config.pad_name_size

    def _build_triangle_body(self) -> None:
        """Build the triangular buffer body shape."""
        th = self.config.tri_height
        tw = self.config.tri_width
        th2 = th / 2.0
        tw2 = tw / 2.0

        # Triangle points: output tip, top input, bottom input, back to output tip
        body_points = [
            (tw2, 0.0),  # Output tip (right point)
            (-tw2, th2),  # Top left point
            (-tw2, -th2),  # Bottom left point
            (tw2, 0.0),  # Back to output tip (closes triangle)
        ]

        if self.config.filled:
            # Use Polygon for filled triangle
            self.triangle_body = Polygon(
                body_points[:-1]
            )  # Remove duplicate closing point
        else:
            # Use Polyline for outline triangle
            self.triangle_body = Polyline(self.config.line_width, body_points)

    def _build_pins(self) -> None:
        """Build input and output pins for the buffer."""
        tw2 = math.floor(self.config.tri_width / 2)

        # Input and output pins
        in_pos = (-tw2, 0)
        out_pos = (tw2, 0)
        in_dir = Direction.Left
        out_dir = Direction.Right

        self.p = {
            1: Pin(at=in_pos, direction=in_dir, length=self.config.pin_length),
            2: Pin(at=out_pos, direction=out_dir, length=self.config.pin_length),
        }

        self.pin_decorators = []
        if self.config.inverter:
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
    def tri_height(self) -> float:
        """See :attr:`~.BufferConfig.tri_height`."""
        return self.config.tri_height

    @property
    def tri_width(self) -> float:
        """See :attr:`~.BufferConfig.tri_width`."""
        return self.config.tri_width

    @property
    def filled(self) -> bool:
        """See :attr:`~.BufferConfig.filled`."""
        return self.config.filled

    @property
    def line_width(self) -> float:
        """See :attr:`~.BufferConfig.line_width`."""
        return self.config.line_width

    @property
    def pin_length(self) -> float:
        """See :attr:`~.BufferConfig.pin_length`."""
        return self.config.pin_length

    @property
    def inverter(self) -> bool:
        """See :attr:`~.BufferConfig.inverter`."""
        return self.config.inverter

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config
