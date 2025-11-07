"""
Test module for inductor symbols functionality.

This module contains comprehensive tests for the inductor symbol implementations.
"""

# Import JITX components for the design
import jitx.test
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.landpattern import Landpattern, Pad
from jitx.net import Port
from jitx.design import Design
from jitx.shapes.primitive import Polygon
from jitx.symbol import SymbolMapping
from jitx.landpattern import PadMapping

# Import our custom inductor symbol
from jitxlib.symbols.context import SymbolStyleContext
from jitxlib.symbols.inductor import (
    InductorSymbol,
    InductorConfig,
    InductorCoreStyle,
)

from examples.defaults.board import DefaultBoard, DefaultSubstrate
from jitxlib.symbols.label import LabelConfig


class InductorPad(Pad):
    shape = Polygon([(-0.3, -0.4), (0.3, -0.4), (0.3, 0.4), (-0.3, 0.4)])


class InductorLandpattern(Landpattern):
    pad1 = InductorPad().at(-1.0, 0)
    pad2 = InductorPad().at(1.0, 0)


class InductorComponent(Component):
    p1 = Port()
    p2 = Port()

    mpn = "IND"
    manufacturer = "Test Co"
    reference_designator_prefix = "L"

    def __init__(self, symbol: InductorSymbol):
        self.symbol = symbol
        self.landpattern = InductorLandpattern()

        self.mappings = [
            SymbolMapping(
                {
                    self.p1: self.symbol.a,
                    self.p2: self.symbol.c,
                }
                if self.symbol.polarized
                else {
                    self.p1: self.symbol.p[1],
                    self.p2: self.symbol.p[2],
                }
            ),
            PadMapping(
                {self.p1: self.landpattern.pad1, self.p2: self.landpattern.pad2}
            ),
        ]


class InductorCircuit(Circuit):
    # =================================================================
    # Demonstration of Different Configuration Methods
    # =================================================================

    # Method 1: Default constructor (using context or built-in defaults)
    default_inductor = InductorComponent(symbol=InductorSymbol())

    # Method 2: Individual parameter overrides using kwargs
    kwargs_inductor = InductorComponent(
        symbol=InductorSymbol(pitch=6.0, line_width=0.1, periods=5)
    )

    # Method 3: Using a configuration object
    config_inductor = InductorComponent(
        symbol=InductorSymbol(
            config=InductorConfig(
                pitch=5.0,
                periods=3,
                line_width=0.08,
                polarized=True,
                core_style=InductorCoreStyle.SINGLE_BAR_CORE,
            )
        )
    )

    # Method 4: Config object + kwargs overrides (kwargs take precedence)
    config_plus_kwargs_inductor = InductorComponent(
        symbol=InductorSymbol(
            config=InductorConfig(pitch=3.0, periods=6),  # Base config
            pitch=7.0,  # Override pitch via kwargs (takes precedence!)
            line_width=0.1,  # Override line_width via kwargs
            core_style=InductorCoreStyle.DOUBLE_BAR_CORE,
        )
    )

    # Method 5: Edge cases and special configurations
    # Demonstrating extreme parameter values and special behaviors
    minimal_inductor = InductorComponent(
        symbol=InductorSymbol(
            pitch=2.0,
            porch_width=0.85,
            periods=1,
            line_width=0.05,
            label_config=LabelConfig(ref_size=0.2),
        )
    )
    large_inductor = InductorComponent(
        symbol=InductorSymbol(
            polarized=True,
            pitch=20.0,
            periods=5,
            line_width=0.5,
            core_style=InductorCoreStyle.SINGLE_BAR_CORE,
            label_config=LabelConfig(ref_size=3.0),
        )
    )
    many_period_inductor = InductorComponent(
        symbol=InductorSymbol(
            pitch=10.0,
            porch_width=1.0,
            periods=10,
            line_width=0.1,
            core_style=InductorCoreStyle.DOUBLE_BAR_CORE,
        )
    )

    def __init__(self):
        self.nets = [
            self.default_inductor.p1 + self.kwargs_inductor.p1,
            self.kwargs_inductor.p1 + self.config_inductor.p1,
            self.config_inductor.p1 + self.config_plus_kwargs_inductor.p1,
            self.config_plus_kwargs_inductor.p1 + self.minimal_inductor.p1,
            self.minimal_inductor.p1 + self.large_inductor.p1,
            self.large_inductor.p1 + self.many_period_inductor.p1,
            self.default_inductor.p2 + self.kwargs_inductor.p2,
            self.kwargs_inductor.p2 + self.config_inductor.p2,
            self.config_inductor.p2 + self.config_plus_kwargs_inductor.p2,
            self.config_plus_kwargs_inductor.p2 + self.minimal_inductor.p2,
            self.minimal_inductor.p2 + self.large_inductor.p2,
            self.large_inductor.p2 + self.many_period_inductor.p2,
        ]


class InductorDesign(Design):
    board = DefaultBoard()
    substrate = DefaultSubstrate()
    symbol_style_context = SymbolStyleContext(
        inductor_config=InductorConfig(
            pitch=4,
            polarized=False,
            porch_width=0.75,
            periods=2,
            line_width=0.25,
        ),
        label_config=LabelConfig(
            ref_size=1.5,
            value_size=1.5,
        ),
    )

    def __init__(self):
        self.circuit = InductorCircuit()


class InductorSymbolTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = InductorDesign()

        import jitx._translate.design

        jitx._translate.design.package_design(design)
