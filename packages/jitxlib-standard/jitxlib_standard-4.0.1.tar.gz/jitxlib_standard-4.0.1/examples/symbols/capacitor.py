"""
Test module for capacitor symbols functionality.

This module contains comprehensive tests for the capacitor symbol implementations,
including basic capacitors and polarized capacitors with different styles.
"""

# Import JITX components for the design
import jitx.test
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.landpattern import Landpattern, Pad
from jitx.net import Port
from jitx.design import Design
from jitx.shapes.primitive import Polygon, Polyline
from jitx.feature import Silkscreen

# Import our custom capacitor symbols
from jitx.units import percent
from jitxlib.symbols.context import SymbolStyleContext
from jitxlib.symbols.capacitor import (
    CapacitorConfig,
    CapacitorSymbol,
    PolarizedCapacitorConfig,
    PolarizedCapacitorSymbol,
    PolarizedStyle,
)

from examples.defaults.board import DefaultBoard, DefaultSubstrate


class CapacitorPad(Pad):
    shape = Polygon([(-0.3, -0.4), (0.3, -0.4), (0.3, 0.4), (-0.3, 0.4)])


class CapacitorLandpattern(Landpattern):
    pad1 = CapacitorPad().at(-1.0, 0)
    pad2 = CapacitorPad().at(1.0, 0)

    # Add silkscreen showing capacitor plates
    silkscreen1 = Silkscreen(
        Polyline(
            0.1,
            [
                # Top plate
                (0.6, -0.2),
                (0.2, -0.2),
                (0.2, 0.2),
                (0.6, 0.2),
            ],
        )
    )

    silkscreen2 = Silkscreen(
        Polyline(
            0.1,
            [
                # Bottom plate
                (-0.6, -0.2),
                (-0.2, -0.2),
                (-0.2, 0.2),
                (-0.6, 0.2),
            ],
        )
    )

    def __init__(self, is_polarized: bool):
        if is_polarized:
            # Add plus sign for polarized capacitors
            self.silkscreen_plus = Silkscreen(
                Polyline(
                    0.1,
                    [
                        (-0.5, 0.4),
                        (-0.3, 0.4),  # horizontal line
                        (-0.4, 0.4),
                        (-0.4, 0.3),
                        (-0.4, 0.5),  # vertical line
                    ],
                )
            )


class CapacitorComponent(Component):
    mpn = "CAP"
    manufacturer = "Test Co"
    reference_designator_prefix = "C"

    def __init__(self, symbol: CapacitorSymbol):
        is_polarized = isinstance(symbol, PolarizedCapacitorSymbol)
        self.symbol = symbol
        self.landpattern = CapacitorLandpattern(is_polarized)

        # Set up ports based on capacitor type
        if is_polarized:
            # Polarized capacitors use a/c ports
            self.a = Port()
            self.c = Port()
        else:
            # Regular capacitors use numbered ports in dictionary
            self.p = {1: Port(), 2: Port()}


class CapacitorCircuit(Circuit):
    # =================================================================
    # Demonstration of Different Configuration Methods
    # =================================================================

    # Method 1: Default constructors (using context or built-in defaults)
    default_capacitor = CapacitorComponent(symbol=CapacitorSymbol())
    default_polarized_straight = CapacitorComponent(symbol=PolarizedCapacitorSymbol())
    default_polarized_curved = CapacitorComponent(
        symbol=PolarizedCapacitorSymbol(
            config=PolarizedCapacitorConfig(style=PolarizedStyle.CURVED)
        )
    )

    # Method 2: Individual parameter overrides using kwargs
    kwargs_capacitor = CapacitorComponent(
        symbol=CapacitorSymbol(pitch=6.0, width=4.0, line_width=0.15)
    )
    kwargs_polarized = CapacitorComponent(
        symbol=PolarizedCapacitorSymbol(
            pitch=5.0, width=3.5, plus_size=0.6, pol_radius=8.0
        )
    )

    # Method 3: Using configuration objects with percentages
    config_capacitor = CapacitorComponent(
        symbol=CapacitorSymbol(
            config=CapacitorConfig(
                pitch=4.5,
                width=2.5,
                porch_width=75 * percent,  # 75% of pitch/2
                line_width=0.5,
            )
        )
    )
    config_polarized_straight = CapacitorComponent(
        symbol=PolarizedCapacitorSymbol(
            config=PolarizedCapacitorConfig(
                pitch=5.0,
                width=3.2,
                style=PolarizedStyle.STRAIGHT,
                porch_width=85 * percent,  # 85% of pitch/2
                plus_size=25 * percent,  # 25% of width
            )
        )
    )
    config_polarized_curved = CapacitorComponent(
        symbol=PolarizedCapacitorSymbol(
            config=PolarizedCapacitorConfig(
                pitch=4.8,
                width=2.8,
                style=PolarizedStyle.CURVED,
                pol_radius=0.8,
                porch_width=90 * percent,  # 90% of pitch/2
                plus_size=30 * percent,  # 30% of width
                line_width=0.1,
            )
        )
    )

    # Method 4: Config object + kwargs overrides (kwargs take precedence)
    config_plus_kwargs_capacitor = CapacitorComponent(
        symbol=CapacitorSymbol(
            config=CapacitorConfig(pitch=3.0, width=2.0),  # Base config
            pitch=7.0,  # Override pitch via kwargs (takes precedence!)
            porch_width=70 * percent,  # Override with percentage
            line_width=0.14,  # Override line_width via kwargs
        )
    )
    config_plus_kwargs_polarized = CapacitorComponent(
        symbol=PolarizedCapacitorSymbol(
            config=PolarizedCapacitorConfig(
                pitch=3.5, style=PolarizedStyle.STRAIGHT
            ),  # Base config
            width=3.0,  # Override width via kwargs
            plus_size=35 * percent,  # Override plus_size with percentage
            style=PolarizedStyle.CURVED,  # Override style via kwargs
        )
    )

    # Method 5: Edge cases and special configurations
    # Demonstrating extreme parameter values and special behaviors
    minimal_capacitor = CapacitorComponent(
        symbol=CapacitorSymbol(pitch=2.0, width=1.5, porch_width=95 * percent)
    )
    wide_line_capacitor = CapacitorComponent(
        symbol=CapacitorSymbol(line_width=0.2, width=4.0)
    )

    # Method 6: Different porch width styles (percentage vs absolute)
    percentage_porch_capacitor = CapacitorComponent(
        symbol=CapacitorSymbol(porch_width=60 * percent)  # 60% of pitch/2
    )
    absolute_porch_capacitor = CapacitorComponent(
        symbol=CapacitorSymbol(porch_width=1.8)  # Absolute value
    )

    def __init__(self):
        self.test_nets = [
            # Parallel connection: All first terminals together
            self.default_capacitor.p[1] + self.kwargs_capacitor.p[1],
            self.kwargs_capacitor.p[1] + self.config_capacitor.p[1],
            self.config_capacitor.p[1] + self.config_plus_kwargs_capacitor.p[1],
            self.config_plus_kwargs_capacitor.p[1] + self.minimal_capacitor.p[1],
            self.minimal_capacitor.p[1] + self.wide_line_capacitor.p[1],
            self.wide_line_capacitor.p[1] + self.percentage_porch_capacitor.p[1],
            self.percentage_porch_capacitor.p[1] + self.absolute_porch_capacitor.p[1],
            self.absolute_porch_capacitor.p[1] + self.default_polarized_straight.a,
            self.default_polarized_straight.a + self.default_polarized_curved.a,
            self.default_polarized_curved.a + self.kwargs_polarized.a,
            self.kwargs_polarized.a + self.config_polarized_straight.a,
            self.config_polarized_straight.a + self.config_polarized_curved.a,
            self.config_polarized_curved.a + self.config_plus_kwargs_polarized.a,
            # Parallel connection: All second terminals together
            self.default_capacitor.p[2] + self.kwargs_capacitor.p[2],
            self.kwargs_capacitor.p[2] + self.config_capacitor.p[2],
            self.config_capacitor.p[2] + self.config_plus_kwargs_capacitor.p[2],
            self.config_plus_kwargs_capacitor.p[2] + self.minimal_capacitor.p[2],
            self.minimal_capacitor.p[2] + self.wide_line_capacitor.p[2],
            self.wide_line_capacitor.p[2] + self.percentage_porch_capacitor.p[2],
            self.percentage_porch_capacitor.p[2] + self.absolute_porch_capacitor.p[2],
            self.absolute_porch_capacitor.p[2] + self.default_polarized_straight.c,
            self.default_polarized_straight.c + self.default_polarized_curved.c,
            self.default_polarized_curved.c + self.kwargs_polarized.c,
            self.kwargs_polarized.c + self.config_polarized_straight.c,
            self.config_polarized_straight.c + self.config_polarized_curved.c,
            self.config_polarized_curved.c + self.config_plus_kwargs_polarized.c,
        ]


class CapacitorDesign(Design):
    board = DefaultBoard()
    substrate = DefaultSubstrate()
    symbol_style_context = SymbolStyleContext(
        capacitor_config=CapacitorConfig(
            porch_width=75 * percent,
            # width=2.0,
            # line_width=0.05,
        ),
        polarized_capacitor_config=PolarizedCapacitorConfig(
            # pitch=4,
            # width=1.5,
            # style=PolarizedStyle.STRAIGHT,
            # pol_radius=5.0,
            # plus_size=0.2,
            # line_width=0.05,
        ),
    )

    def __init__(self):
        self.circuit = CapacitorCircuit()


class CapacitorSymbolTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = CapacitorDesign()

        import jitx._translate.design

        jitx._translate.design.package_design(design)
