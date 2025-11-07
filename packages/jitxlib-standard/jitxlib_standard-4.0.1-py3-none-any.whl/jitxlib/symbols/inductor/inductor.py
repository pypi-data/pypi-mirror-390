"""
Inductor symbol for JITX Standard Library

This module provides the inductor symbol definition that also
supports the transformer symbol definition.
"""

from __future__ import annotations
import math
from enum import Enum
from dataclasses import dataclass, replace

from jitx.shapes.primitive import Arc, ArcPolyline, Polyline
from jitx.symbol import Direction, Pin

from ..common import DEF_LINE_WIDTH
from ..label import LabelConfigurable, LabelledSymbol


class InductorCoreStyle(Enum):
    """Inductor core styles"""

    NO_CORE = "no_core"
    SINGLE_BAR_CORE = "single_bar_core"
    DOUBLE_BAR_CORE = "double_bar_core"


# Inductor constants
DEF_IND_PITCH = 4.0
DEF_IND_CORE_STYLE = InductorCoreStyle.NO_CORE
DEF_IND_PORCH_WIDTH = 0.25
DEF_IND_PERIODS = 3


@dataclass
class InductorConfig(LabelConfigurable):
    """
    Configuration for inductor symbols

    Defines the geometric and visual parameters for inductor symbols.
    """

    pitch: float = DEF_IND_PITCH
    """Distance between pin points"""
    polarized: bool = False
    """Whether the inductor has polarity"""
    core_style: InductorCoreStyle = DEF_IND_CORE_STYLE
    """Style of the inductor core"""
    porch_width: float = DEF_IND_PORCH_WIDTH
    """Length of straight sections at ends"""
    periods: int = DEF_IND_PERIODS
    """Number of half-circles in the inductor winding shape"""
    line_width: float = DEF_LINE_WIDTH
    """Width of the inductor lines"""


class InductorSymbol(LabelledSymbol):
    """Inductor symbol with graphics and pins."""

    config: InductorConfig

    inductor_bars: tuple[()] | tuple[Polyline] | tuple[Polyline, Polyline]
    inductor_coils: ArcPolyline
    inductor_porches: tuple[Polyline, Polyline]

    def __init__(
        self,
        config: InductorConfig | None = None,
        partial_symbol: bool = False,
        **kwargs,
    ):
        """
        Initialize inductor symbol

        Args:
            config: Config object, or None to use defaults
            partial_symbol: Whether to build a partial symbol (no pins or labels)
            **kwargs: Individual parameters to override defaults
        """
        from ..context import SymbolStyleContext

        context = SymbolStyleContext.get()

        if config is None:
            if context is None:
                config = InductorConfig()
            else:
                config = context.inductor_config

        self.config = replace(config, **kwargs)
        self._build_artwork()

        # Skip pins and labels if requested:
        if not partial_symbol:
            self._build_pins()
            self._build_labels(ref=Direction.Right, value=Direction.Right)

    def _build_artwork(self) -> None:
        """Build the coil glyphs for an inductor based on inductors.stanza."""
        w = math.floor(self.pitch / 2)

        if self.porch_width > w:
            raise ValueError(
                f"Inductor porch width {self.porch_width} cannot be greater than half the pitch rounded down ({w} = math.floor({self.pitch}/2))"
            )

        circ_start = w - self.porch_width
        circ_len = 2 * circ_start
        diameter = circ_len / self.periods
        radius = diameter / 2.0

        # Front and back porches
        self.inductor_porches = (
            Polyline(self.line_width, [(0, -circ_start), (0, -w)]),
            Polyline(self.line_width, [(0, w), (0, circ_start)]),
        )

        # Coils (series of semi-circles)
        arcs = []
        for i in range(self.periods):
            center_y = circ_start - radius - (i * diameter)
            arcs.append(Arc((0, center_y), radius, 90.0, 180.0))

        self.inductor_coils = ArcPolyline(self.line_width, arcs)

        # Core bars
        line_margin = 3 * self.line_width
        core_x = -(radius + line_margin)
        if self.config.core_style == InductorCoreStyle.SINGLE_BAR_CORE:
            self.inductor_bars = (
                Polyline(
                    self.line_width, [(core_x, circ_start), (core_x, -circ_start)]
                ),
            )
        elif self.config.core_style == InductorCoreStyle.DOUBLE_BAR_CORE:
            self.inductor_bars = (
                Polyline(
                    self.line_width, [(core_x, circ_start), (core_x, -circ_start)]
                ),
                Polyline(
                    self.line_width,
                    [
                        (core_x - line_margin, circ_start),
                        (core_x - line_margin, -circ_start),
                    ],
                ),
            )

    def _build_pins(self):
        """
        Build symbol pins for the inductor

        Creates appropriate pins based on polarity setting.
        Polarized inductors get 'a' (anode) and 'c' (cathode) pins,
        Non-polarized inductors get generic 'p[1]' and 'p[2]' pins.
        """
        w = math.floor(self.pitch / 2)
        if self.polarized:
            self.a = Pin(at=(0, w), direction=Direction.Up)
            self.c = Pin(at=(0, -w), direction=Direction.Down)
        else:
            self.p = [
                None,  # Having an empty entry increments pin index.
                Pin(at=(0, w), direction=Direction.Up),
                Pin(at=(0, -w), direction=Direction.Down),
            ]

    # Convenience properties to access config values
    @property
    def pitch(self) -> float:
        """See :attr:`~.InductorConfig.pitch`."""
        return self.config.pitch

    @property
    def polarized(self) -> bool:
        """See :attr:`~.InductorConfig.polarized`."""
        return self.config.polarized

    @property
    def porch_width(self) -> float:
        """See :attr:`~.InductorConfig.porch_width`."""
        return self.config.porch_width

    @property
    def periods(self) -> int:
        """See :attr:`~.InductorConfig.periods`."""
        return self.config.periods

    @property
    def line_width(self) -> float:
        """See :attr:`~.InductorConfig.line_width`."""
        return self.config.line_width

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config
