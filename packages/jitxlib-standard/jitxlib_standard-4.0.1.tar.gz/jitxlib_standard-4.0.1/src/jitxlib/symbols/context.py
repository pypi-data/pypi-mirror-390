"""
Resistor style context for JITX Standard Library

This module provides global configuration context for resistor symbols,
allowing consistent styling across all resistor types in a design or a portion thereof.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from jitx.context import Context

from .arrow import ArrowConfig
from .box import BoxConfig
from .decorators import DecoratorConfig
from .label import LabelConfig
from .resistor.resistor import ResistorConfig, ResistorStyle
from .resistor.photo import PhotoResistorConfig
from .resistor.variable import VariableResistorConfig
from .resistor.potentiometer import PotentiometerConfig
from .inductor.inductor import InductorConfig
from .capacitor.capacitor import (
    CapacitorConfig,
    PolarizedCapacitorConfig,
)
from .logic.and_gate import ANDGateConfig
from .logic.or_gate import ORGateConfig
from .logic.buffer import BufferConfig
from .net_symbols.ground import GroundConfig
from .net_symbols.power import PowerConfig


@dataclass
class SymbolStyleContext(Context):
    """
    Symbol Style Context

    Provides centralized configuration for all symbol types.
    This allows setting consistent visual styles and default
    parameters across an entire design or a portion thereof.
    """

    resistor_style: ResistorStyle = ResistorStyle.TRIANGLE_WAVE
    """Visual style for all resistor symbols"""
    resistor_config: ResistorConfig = field(default_factory=ResistorConfig)
    """Default configuration for basic resistors"""
    photo_resistor_config: PhotoResistorConfig = field(
        default_factory=PhotoResistorConfig
    )
    """Default configuration for photo resistors"""
    variable_resistor_config: VariableResistorConfig = field(
        default_factory=VariableResistorConfig
    )
    """Default configuration for variable resistors"""
    potentiometer_config: PotentiometerConfig = field(
        default_factory=PotentiometerConfig
    )
    """Default configuration for potentiometers"""
    inductor_config: InductorConfig = field(default_factory=InductorConfig)
    """Default configuration for inductors"""
    arrow_config: ArrowConfig = field(default_factory=ArrowConfig)
    """Default configuration for arrows"""
    label_config: LabelConfig = field(default_factory=LabelConfig)
    """Default configuration for reference designator and value labels"""
    box_config: BoxConfig = field(default_factory=BoxConfig)
    """Default configuration for symbol boxes"""
    decorator_config: DecoratorConfig = field(default_factory=DecoratorConfig)
    """Default configuration for pin decorators"""

    capacitor_config: CapacitorConfig = field(default_factory=CapacitorConfig)
    """Default configuration for capacitors"""
    polarized_capacitor_config: PolarizedCapacitorConfig = field(
        default_factory=PolarizedCapacitorConfig
    )
    """Default configuration for polarized capacitors"""

    and_gate_config: ANDGateConfig = field(default_factory=ANDGateConfig)
    """Default configuration for AND gates"""
    or_gate_config: ORGateConfig = field(default_factory=ORGateConfig)
    """Default configuration for OR gates"""
    buffer_config: BufferConfig = field(default_factory=BufferConfig)
    """Default configuration for buffers"""

    ground_config: GroundConfig = field(default_factory=GroundConfig)
    """Default configuration for ground symbols"""

    power_config: PowerConfig = field(default_factory=PowerConfig)
    """Default configuration for power symbols"""
