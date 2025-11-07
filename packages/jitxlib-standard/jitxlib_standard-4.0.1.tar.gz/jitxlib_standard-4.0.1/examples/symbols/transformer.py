"""
Test module for transformer symbols functionality.

This module contains comprehensive tests for the transformer symbol implementations.
"""

# Import JITX components for the design
from jitx._structural import pathstring
from jitx.inspect import visit
import jitx.test
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.landpattern import Landpattern, Pad
from jitx.net import Port
from jitx.design import Design
from jitx.shapes.primitive import Polygon, Polyline
from jitx.feature import Silkscreen
from jitx.symbol import Pin, SymbolMapping, Direction
from jitx.landpattern import PadMapping

# Import our custom transformer symbol
from jitxlib.symbols.label import LabelConfig
from jitxlib.symbols.transformer.transformer import (
    TransformerSymbol,
    TransformerConfig,
    InductorCoreStyle,
    CoilConfig,
)
from jitxlib.symbols.inductor import InductorConfig

from examples.defaults.board import DefaultBoard, DefaultSubstrate


class TransformerPad(Pad):
    shape = Polygon([(-0.3, -0.4), (0.3, -0.4), (0.3, 0.4), (-0.3, 0.4)])


class TransformerLandpattern(Landpattern):
    def __init__(self, num_coils: int = 2, taps_per_coil: list[int] | None = None):
        if taps_per_coil is None:
            taps_per_coil = [0] * num_coils

        pins = 1

        # Create main pads for each coil
        for i in range(num_coils):
            setattr(self, f"p[{pins}]", TransformerPad().at(-1.0, 2.0 * i))
            setattr(self, f"p[{pins + 1}]", TransformerPad().at(1.0, 2.0 * i))
            pins += 2

            # Create tap pads if any
            for j in range(taps_per_coil[i]):
                setattr(
                    self,
                    f"p[{pins + j}]",
                    TransformerPad().at(0.0, 2.0 * i + 0.5 + j * 0.5),
                )
            pins += taps_per_coil[i]

        # Add silkscreen showing transformer body
        self.silkscreen = Silkscreen(
            Polyline(
                0.1,
                [
                    (-0.8, 0.3),
                    (-0.4, 0.3),
                    (-0.2, -0.3),
                    (0.0, 0.3),
                    (0.2, -0.3),
                    (0.4, 0.3),
                    (0.8, 0.3),
                ],
            )
        )


class TransformerComponent(Component):
    mpn = "TRF"
    manufacturer = "Test Co"
    reference_designator_prefix = "T"

    def __init__(self, symbol: TransformerSymbol):
        self.symbol = symbol

        # Count taps per coil
        taps_per_coil = [len(coil.taps) for coil in symbol.config.coils]

        # Create landpattern with appropriate number of coils and taps
        self.landpattern = TransformerLandpattern(
            num_coils=len(symbol.coils), taps_per_coil=taps_per_coil
        )

        # Create ports for each coil and its taps
        # Create symbol and pad mappings
        symbol_mapping = {}
        pad_mapping = {}
        for i, (trace, pin) in enumerate(visit(symbol, Pin)):
            port = Port()
            setattr(self, pathstring(trace.path), port)
            symbol_mapping[port] = pin
            pad_mapping[port] = getattr(self.landpattern, f"p[{i + 1}]")

        self.mappings = (SymbolMapping(symbol_mapping), PadMapping(pad_mapping))


class TransformerCircuit(Circuit):
    # =================================================================
    # Demonstration of Different Configuration Methods
    # =================================================================

    # Test transformers from Stanza definitions
    ind_config_1_1 = InductorConfig(porch_width=0.0, periods=4, line_width=0.1)
    ind_config_1_2 = InductorConfig(porch_width=0.0, periods=6, line_width=0.1)
    t1 = TransformerComponent(
        symbol=TransformerSymbol(
            config=TransformerConfig(
                coils=[
                    CoilConfig(
                        config=ind_config_1_1,
                        direction=Direction.Left,
                        polarized=Direction.Up,
                        taps=(1,),
                    ),
                    CoilConfig(
                        config=ind_config_1_2,
                        direction=Direction.Right,
                        polarized=Direction.Up,
                        taps=(3,),
                    ),
                    CoilConfig(
                        config=ind_config_1_1,
                        direction=Direction.Left,
                        polarized=Direction.Up,
                    ),
                    CoilConfig(
                        config=ind_config_1_1,
                        direction=Direction.Right,
                        polarized=Direction.Up,
                    ),
                ],
                core_style=InductorCoreStyle.DOUBLE_BAR_CORE,
                pin_pitch=4.0,
            )
        )
    )

    ind_config_2_1 = InductorConfig(porch_width=0.0, periods=4, line_width=0.1)
    ind_config_2_2 = InductorConfig(porch_width=0.0, periods=6, line_width=0.1)
    t2 = TransformerComponent(
        symbol=TransformerSymbol(
            config=TransformerConfig(
                coils=[
                    CoilConfig(
                        config=ind_config_2_1,
                        direction=Direction.Left,
                        polarized=Direction.Up,
                        taps=(1,),
                    ),
                    CoilConfig(
                        config=ind_config_2_2,
                        direction=Direction.Right,
                        polarized=Direction.Down,
                    ),
                ],
                core_style=InductorCoreStyle.NO_CORE,
                pin_pitch=2.0,
            )
        )
    )

    ind_config_3_1 = InductorConfig(porch_width=1.0, periods=4, line_width=0.2)
    ind_config_3_2 = InductorConfig(porch_width=1.0, periods=4, line_width=0.2)
    t3 = TransformerComponent(
        symbol=TransformerSymbol(
            config=TransformerConfig(
                coils=[
                    CoilConfig(
                        config=ind_config_3_1,
                        direction=Direction.Left,
                        polarized=Direction.Down,
                    ),
                    CoilConfig(
                        config=ind_config_3_2,
                        direction=Direction.Right,
                        polarized=Direction.Down,
                    ),
                ],
                core_style=InductorCoreStyle.SINGLE_BAR_CORE,
                pin_pitch=3.0,
                label_config=LabelConfig(ref_size=2.0, value_size=2.0),
            )
        )
    )


class TransformerDesign(Design):
    board = DefaultBoard()
    substrate = DefaultSubstrate()

    def __init__(self):
        self.circuit = TransformerCircuit()


class TransformerSymbolTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = TransformerDesign()

        import jitx._translate.design

        jitx._translate.design.package_design(design)
