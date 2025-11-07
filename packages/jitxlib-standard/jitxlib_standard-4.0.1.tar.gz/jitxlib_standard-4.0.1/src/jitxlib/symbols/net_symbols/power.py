"""
Power symbol for JITX Standard Library

This module defines the Power symbol, often used as a net symbol, and associated construction functions.
"""

from __future__ import annotations
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from jitx.compat.altium import AltiumSymbol, AltiumSymbolProperty
from jitx.shapes import Shape
from jitx.shapes.primitive import Polyline
from jitx.symbol import Direction, Pin, SymbolOrientation

from ..common import DEF_LINE_WIDTH
from ..label import LabelConfigurable, LabelledSymbol

if TYPE_CHECKING:
    from ..context import SymbolStyleContext


DEF_PWR_PORCH_WIDTH = 1.0
DEF_PWR_BAR_WIDTH = 3.0


@dataclass
class PowerConfig(LabelConfigurable):
    """
    Configuration for power symbols

    Defines the geometric and visual parameters for power symbols.
    """

    line_width: float = DEF_LINE_WIDTH
    """Width of the power symbol lines"""
    porch_width: float = DEF_PWR_PORCH_WIDTH
    """Distance from pin to horizontal bar"""
    bar_width: float = DEF_PWR_BAR_WIDTH
    """Width of the horizontal power bar"""

    def __post_init__(self):
        """Validate configuration parameters"""
        if self.line_width <= 0:
            raise ValueError("Power symbol line_width must be positive")
        if self.porch_width <= 0:
            raise ValueError("Power symbol porch_width must be positive")
        if self.bar_width <= 0:
            raise ValueError("Power symbol bar_width must be positive")


class PowerSymbol(LabelledSymbol):
    """
    Power symbol with graphics and pin.

    Creates a typical power net symbol consisting of a vertical line
    with a horizontal bar at the top in the +Y dimension.
    """

    config: PowerConfig
    vertical_line: Shape[Polyline]
    horizontal_bar: Shape[Polyline]
    pwr: Pin

    def _lookup_config(
        self,
        config: PowerConfig | None = None,
        context: SymbolStyleContext | None = None,
    ) -> PowerConfig:
        """Lookup the config for this symbol."""
        if config is None:
            if context is None:
                return PowerConfig()
            return context.power_config
        return config

    def __init__(self, config: PowerConfig | None = None, **kwargs):
        """
        Initialize power symbol

        Args:
            config: PowerConfig, or None to use defaults
            **kwargs: Individual parameters to override defaults
        """
        # Apparently this needs to be imported here, even though SymbolStyleContext is imported in TYPE_CHECKING.
        from ..context import SymbolStyleContext

        context = SymbolStyleContext.get()
        config = self._lookup_config(config, context)
        self.config = replace(config, **kwargs)

        self._build_power_symbol()
        self._build_pins()
        self._build_labels(value=Direction.Up)
        self.orientation = SymbolOrientation(0)
        AltiumSymbolProperty(AltiumSymbol.PowerBar).assign(self)

    def _build_pins(self) -> None:
        """Build 'pwr' symbol pin for the power."""
        self.pwr = Pin(at=(0, 0), direction=Direction.Down)

    def _build_power_symbol(self) -> None:
        """Build the power symbol artwork."""
        # Vertical line from pin to horizontal bar
        self.vertical_line = Polyline(
            self.config.line_width,
            [(0.0, 0.0), (0.0, self.config.porch_width)],
        )

        # Horizontal bar at the top
        half_bar_width = self.config.bar_width / 2.0
        self.horizontal_bar = Polyline(
            self.config.line_width,
            [
                (-half_bar_width, self.config.porch_width),
                (half_bar_width, self.config.porch_width),
            ],
        )

    # Convenience properties to access config values
    @property
    def line_width(self) -> float:
        """See :attr:`~.PowerConfig.line_width`."""
        return self.config.line_width

    @property
    def porch_width(self) -> float:
        """See :attr:`~.PowerConfig.porch_width`."""
        return self.config.porch_width

    @property
    def bar_width(self) -> float:
        """See :attr:`~.PowerConfig.bar_width`."""
        return self.config.bar_width

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config


SupplySymbol = PowerSymbol
