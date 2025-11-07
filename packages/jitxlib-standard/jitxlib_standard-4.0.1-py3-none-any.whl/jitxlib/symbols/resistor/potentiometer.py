"""
Potentiometer symbols for JITX Standard Library

This module provides potentiometer symbol definitions with wiper pins.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, override

from jitx.symbol import Direction, Pin
from ..arrow import Arrow, ArrowConfigurable
from .resistor import (
    ResistorSymbol,
    ResistorConfig,
)

if TYPE_CHECKING:
    from ..context import SymbolStyleContext


@dataclass
class PotentiometerConfig(ResistorConfig, ArrowConfigurable):
    """Configuration for potentiometer symbols"""


class PotentiometerSymbol(ResistorSymbol):
    """Potentiometer symbol with graphics, wiper arrow, and pins including wiper pin"""

    arrow: Arrow
    wiper: Pin

    @override
    def _symbol_style_config(
        self, context: SymbolStyleContext | None = None
    ) -> PotentiometerConfig:
        """Symbol style config for this potentiometer symbol."""
        if context is None:
            return PotentiometerConfig()
        else:
            return context.potentiometer_config

    def __init__(self, config: PotentiometerConfig | None = None, **kwargs):
        """
        Initialize potentiometer symbol

        Args:
            config: PotentiometerConfig object, or None to use defaults
            **kwargs: Individual parameters to override defaults
        """
        super().__init__(config=config, **kwargs)
        self._build_wiper_pin()

    @override
    def _build_artwork(self):
        """Build the artwork for the potentiometer symbol."""
        # Calculate arrow position and dimensions
        w_start = self.amplitude
        w_end = self.pitch / 2
        shaft_length = abs(w_end - w_start)

        # Create a new config with the correct shaft length for the photo arrows
        config = replace(self.config.get_arrow_config(), shaft_length=shaft_length)

        # Add the diagonal arrow with calculated shaft length
        self.arrow = Arrow((-w_start, 0.0), 180.0, config)

    def _build_wiper_pin(self):
        """Build the wiper pin for the potentiometer symbol."""
        # Floor keeps the pins on the grid.
        w = math.floor(self.pitch / 2)
        self.wiper = Pin(at=(-w, 0), direction=Direction.Left)
