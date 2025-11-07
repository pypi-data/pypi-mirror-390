"""
Test module for logic symbols functionality.

This module contains comprehensive tests for the logic symbol implementations,
including AND, OR, XOR, NAND, NOR, XNOR, Buffer, and Inverter gates.
"""

# Import JITX components for the design
from collections.abc import Sequence
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.inspect import extract
from jitx.landpattern import Landpattern, Pad
from jitx.net import Port
from jitx.design import Design
from jitx.shapes.primitive import Polygon, Polyline
from jitx.feature import Silkscreen

# Import our custom logic symbols
from jitx.symbol import Pin, Symbol
from jitxlib.symbols.decorators import OpenCollectorType
from jitxlib.symbols.logic import (
    ANDGateSymbol,
    ORGateSymbol,
    BufferSymbol,
)

from examples.defaults.board import DefaultBoard, DefaultSubstrate


class LogicPad(Pad):
    shape = Polygon([(-0.2, -0.3), (0.2, -0.3), (0.2, 0.3), (-0.2, 0.3)])


class LogicLandpattern(Landpattern):
    def __init__(self, num_ports: int):
        self.p = {}
        # Input pads on the left
        for i in range(num_ports - 1):
            y_pos = (num_ports - 1) * 0.5 - i * 1.0
            self.p[i + 1] = LogicPad().at(-2.0, y_pos)

        # Output pad on the right
        self.p[num_ports] = LogicPad().at(2.0, 0.0)

        # Add basic silkscreen outline
        outline_points = [
            (-1.5, 1.0),
            (1.5, 1.0),
            (1.5, -1.0),
            (-1.5, -1.0),
            (-1.5, 1.0),
        ]
        self.silkscreen = Silkscreen(Polyline(0.1, outline_points))


class LogicComponent(Component):
    manufacturer = "Test Co"
    reference_designator_prefix = "U"
    mpn = "74LS24211"

    def __init__(self, symbol: Symbol | Sequence[Symbol]):
        if isinstance(symbol, Symbol):
            self.symbol = symbol
            num_pins = len(tuple(extract(self.symbol, Pin)))
        else:
            self.symbol = tuple(symbol)
            num_pins = sum([len(tuple(extract(s, Pin))) for s in self.symbol])

        self.landpattern = LogicLandpattern(num_pins)
        self.p = {i + 1: Port() for i in range(num_pins)}


class LogicCircuit(Circuit):
    # Buffer
    buffer = LogicComponent(BufferSymbol())

    # Inverter
    inverter = LogicComponent(BufferSymbol(inverter=True))

    # AND Gates
    and_gate = LogicComponent(ANDGateSymbol(filled=False))
    nand_gate = LogicComponent(ANDGateSymbol(inverted=True))
    multi_and_gate = LogicComponent(
        (ANDGateSymbol(num_inputs=2), ANDGateSymbol(num_inputs=2))
    )
    nand3_gate = LogicComponent(
        ANDGateSymbol(num_inputs=3, pin_pitch=1.0, inverted=True, filled=False)
    )
    crazy_and_gate = LogicComponent(
        ANDGateSymbol(num_inputs=8, pin_pitch=1.5, height=11.0)
    )

    # OR Gates
    or_gate = LogicComponent(ORGateSymbol())
    nor_gate = LogicComponent(ORGateSymbol(inverted=True))
    xor_gate = LogicComponent(
        ORGateSymbol(exclusive=True, open_collector=OpenCollectorType.SINK)
    )
    nor3_gate = LogicComponent(ORGateSymbol(num_inputs=3, pin_pitch=1.0, inverted=True))
    crazy_or_gate = LogicComponent(
        ORGateSymbol(
            num_inputs=11,
            pin_pitch=1.25,
            height=15.0,
            filled=False,
            open_collector=OpenCollectorType.SINK,
        )
    )


class LogicDesign(Design):
    board = DefaultBoard()
    substrate = DefaultSubstrate()

    def __init__(self):
        self.circuit = LogicCircuit()
