"""
Variable resistor symbols for JITX Standard Library

This module provides variable resistor symbol definitions with diagonal arrows.
"""

from __future__ import annotations
from dataclasses import dataclass, replace
import math
from typing import TYPE_CHECKING, override

from ..arrow import Arrow, ArrowConfigurable
from .resistor import (
    ResistorConfig,
    ResistorSymbol,
)

if TYPE_CHECKING:
    from ..context import SymbolStyleContext

# VariableResistorConfig constants
DEF_VAR_ARROW_SPAN = 3


@dataclass
class VariableResistorConfig(ResistorConfig, ArrowConfigurable):
    """Configuration for variable resistor symbols"""

    arrow_span: float = DEF_VAR_ARROW_SPAN
    """Multiplier on body width for arrow span"""


class VariableResistorSymbol(ResistorSymbol[VariableResistorConfig]):
    """Variable resistor symbol with graphics, adjustment arrow, and pins."""

    arrow: Arrow

    @override
    def _symbol_style_config(
        self, context: SymbolStyleContext | None = None
    ) -> VariableResistorConfig:
        """Symbol style config for this variable resistor symbol."""
        if context is None:
            return VariableResistorConfig()
        else:
            return context.variable_resistor_config

    @override
    def _build_artwork(self):
        """Build the artwork for the variable resistor symbol."""
        # Calculate arrow position and dimensions
        amp = self.amplitude
        porch = self.porch_width
        aw = self.arrow_span
        x = 2 * amp * aw
        y = self.pitch - (2 * porch)

        shaft_length = math.sqrt(x**2 + y**2)
        start = (x / 2, y / 2)
        angle = math.degrees(math.atan2(-y, -x))

        # Create custom arrow config with calculated shaft length
        config = replace(self.config.get_arrow_config(), shaft_length=shaft_length)

        # Add the diagonal arrow
        self.arrow = Arrow(start, angle, config)

    # Convenience properties to access config values
    @property
    def arrow_span(self) -> float:
        """See :attr:`~.VariableResistorConfig.arrow_span`."""
        return self.config.arrow_span
