"""
Basic resistor symbol for JITX Standard Library

This module provides the basic resistor symbol definition that serves
as the foundation for all resistor symbol types.
"""

from __future__ import annotations
import math
from enum import Enum
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, cast

from jitx.shapes import Shape
from jitx.shapes.primitive import Polyline
from jitx.symbol import Direction, Pin

from jitxlib.geometry.linerectangle import line_rectangle

from ..common import DEF_LINE_WIDTH
from ..label import LabelConfigurable, LabelledSymbol

if TYPE_CHECKING:
    from ..context import SymbolStyleContext


class ResistorStyle(Enum):
    """
    Resistor symbol styles

    Defines the visual representation style for resistor symbols.
    """

    TRIANGLE_WAVE = "triangle_wave"  # American zigzag style
    OPEN_RECTANGLE = "open_rectangle"  # European rectangular style


# ResistorConfig constants
DEF_RES_PITCH = 4.0
DEF_RES_PORCH_WIDTH = 0.5
DEF_RES_AMPLITUDE = 0.5
DEF_RES_PERIODS = 3.0


@dataclass
class ResistorConfig(LabelConfigurable):
    """
    Configuration for resistor symbols

    Defines the geometric and visual parameters for resistor symbols.
    """

    pitch: float = DEF_RES_PITCH
    """Distance between pin points"""
    porch_width: float = DEF_RES_PORCH_WIDTH
    """Length of straight sections at ends"""
    amplitude: float = DEF_RES_AMPLITUDE
    """Height/width of the resistor body"""
    periods: float = DEF_RES_PERIODS
    """Number of zigzag periods for triangle wave style"""
    line_width: float = DEF_LINE_WIDTH
    """Width of the resistor lines"""


class ResistorSymbol[T: ResistorConfig](LabelledSymbol):
    """
    Resistor symbol with graphics and pins.
    Also serves as the base class for all other resistor symbol types.
    """

    config: T
    resistor_body: Shape[Polyline]
    resistor_porches: tuple[Shape[Polyline], Shape[Polyline]]

    def _symbol_style_config(self, context: SymbolStyleContext | None = None) -> T:
        """Symbol style config for this resistor symbol."""
        if context is None:
            config = ResistorConfig()
        else:
            config = context.resistor_config
        # Casting necessary because ResistorSymbol is both a generic and a concrete class.
        return cast(T, config)

    def _lookup_config(
        self, config: T | None = None, context: SymbolStyleContext | None = None
    ) -> T:
        """Lookup the config for this symbol."""

        if config is None:
            return self._symbol_style_config(context)
        return config

    # TODO: Look into making kwargs type-specific using a paramspec (same for capacitor class).
    def __init__(self, config: T | None = None, **kwargs):
        """
        Initialize resistor symbol

        Args:
            config: Config object, or None to use defaults
            **kwargs: Individual parameters to override defaults
        """

        # Apparently this needs to be imported here, even though SymbolStyleContext is imported in TYPE_CHECKING.
        from ..context import SymbolStyleContext

        context = SymbolStyleContext.get()
        config = self._lookup_config(config, context)
        self.config = replace(config, **kwargs)

        # By default, use TRIANGLE_WAVE resistor style.
        if context is None:
            style = ResistorStyle.TRIANGLE_WAVE
        else:
            style = context.resistor_style

        if style == ResistorStyle.TRIANGLE_WAVE:
            self._build_triangle_wave_glyphs()
        elif style == ResistorStyle.OPEN_RECTANGLE:
            self._build_open_rectangle_glyphs()
        else:
            raise ValueError(f"Invalid resistor style: {style}")

        self._build_pins()
        self._build_artwork()
        self._build_labels(ref=Direction.Right, value=Direction.Right)

    def _build_artwork(self) -> None:
        """Build the artwork for the resistor symbol, apart from the zigzag or rectangle."""
        pass

    def _build_pins(self) -> None:
        """Build 'p[1]' and 'p[2]' symbol pins for the resistor."""
        # Floor keeps the pins on the grid.
        w = math.floor(self.pitch / 2)
        self.p = {
            1: Pin(at=(0, w), direction=Direction.Up),
            2: Pin(at=(0, -w), direction=Direction.Down),
        }

    def _build_triangle_wave_glyphs(self) -> None:
        """Build triangle wave glyphs for a zigzag resistor."""
        w = math.floor(self.pitch / 2)
        tri_start = w - self.porch_width
        total_w = 2 * tri_start
        period_w = total_w / self.periods
        x_lookup = [0, self.amplitude, 0, -self.amplitude]

        points = []
        points.append((0, -tri_start))

        quarter_periods = int(2 * math.ceil(self.periods / 0.5))
        for i in range(quarter_periods):
            y = i * (period_w / 4) - tri_start
            x = x_lookup[i % 4]
            points.append((x, y))

        points.append((0, tri_start))

        self.resistor_body = Polyline(self.line_width, points)
        self.resistor_porches = (
            Polyline(self.line_width, [(0, -w), points[0]]),
            Polyline(self.line_width, [points[-1], (0, w)]),
        )

    def _build_open_rectangle_glyphs(self) -> None:
        """Build open rectangle glyphs for a rectangular resistor."""
        w = math.floor(self.pitch / 2)
        tri_start = w - self.porch_width
        total_w = 2 * tri_start

        self.resistor_body = line_rectangle(
            2 * self.amplitude, total_w, self.line_width
        )
        self.resistor_porches = (
            Polyline(self.line_width, [(0, -w), (0, -tri_start)]),
            Polyline(self.line_width, [(0, tri_start), (0, w)]),
        )

    # Convenience properties to access config values
    @property
    def pitch(self) -> float:
        """See :attr:`~.ResistorConfig.pitch`."""
        return self.config.pitch

    @property
    def porch_width(self) -> float:
        """See :attr:`~.ResistorConfig.porch_width`."""
        return self.config.porch_width

    @property
    def amplitude(self) -> float:
        """See :attr:`~.ResistorConfig.amplitude`."""
        return self.config.amplitude

    @property
    def periods(self) -> float:
        """See :attr:`~.ResistorConfig.periods`."""
        return self.config.periods

    @property
    def line_width(self) -> float:
        """See :attr:`~.ResistorConfig.line_width`."""
        return self.config.line_width

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config
