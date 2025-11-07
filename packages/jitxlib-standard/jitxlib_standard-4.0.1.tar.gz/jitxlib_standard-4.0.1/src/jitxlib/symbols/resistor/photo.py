"""
Photo resistor symbols for JITX Standard Library

This module provides photoresistor symbol definitions with light arrows.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from ..arrow import Arrow, ArrowConfigurable
from .resistor import (
    ResistorConfig,
    ResistorSymbol,
)

if TYPE_CHECKING:
    from ..context import SymbolStyleContext

# PhotoResistorConfig constants
DEF_PHOTO_ARROW_MARGIN = 0.4
DEF_PHOTO_ARROW_PITCH = 1.0
DEF_PHOTO_ARROW_ANGLE = 45.0
DEF_PHOTO_ARROW_LENGTH = 0.6
DEF_PHOTO_ARROW_WIDTH = 0.2


@dataclass
class PhotoResistorConfig(ResistorConfig, ArrowConfigurable):
    """
    Configuration for photoresistor symbols

    Extends ResistorConfig with photo-specific arrow parameters.
    """

    arrow_margin: float = DEF_PHOTO_ARROW_MARGIN
    """Distance from resistor body to arrows"""
    arrow_pitch: float = DEF_PHOTO_ARROW_PITCH
    """Vertical spacing between arrows"""
    arrow_angle: float = DEF_PHOTO_ARROW_ANGLE
    """Angle of incoming light arrows in degrees"""


class PhotoResistorSymbol(ResistorSymbol):
    """
    Photoresistor symbol with graphics, light arrows, and pins.
    """

    arrows: tuple[Arrow, Arrow]

    @override
    def _symbol_style_config(
        self, context: SymbolStyleContext | None = None
    ) -> PhotoResistorConfig:
        """Symbol style config for this photoresistor symbol."""
        if context is None:
            return PhotoResistorConfig()
        else:
            return context.photo_resistor_config

    @override
    def _build_artwork(self):
        """Build the artwork for the photoresistor symbol."""
        # Calculate arrow positions
        amp = self.amplitude
        margin = self.config.arrow_margin
        y_offset = self.config.arrow_pitch / 2.0
        angle = self.config.arrow_angle

        # Add two arrows using the ArrowSymbol functionality
        arrow_config = self.config.get_arrow_config()
        self.arrows = (
            Arrow((amp + margin, y_offset), angle, arrow_config),
            Arrow((amp + margin, -y_offset), angle, arrow_config),
        )

    # Convenience properties
    @property
    def arrow_margin(self) -> float:
        """See :attr:`~.PhotoResistorConfig.arrow_margin`."""
        return self.config.arrow_margin

    @property
    def arrow_pitch(self) -> float:
        """See :attr:`~.PhotoResistorConfig.arrow_pitch`."""
        return self.config.arrow_pitch

    @property
    def arrow_angle(self) -> float:
        """See :attr:`~.PhotoResistorConfig.arrow_angle`."""
        return self.config.arrow_angle
