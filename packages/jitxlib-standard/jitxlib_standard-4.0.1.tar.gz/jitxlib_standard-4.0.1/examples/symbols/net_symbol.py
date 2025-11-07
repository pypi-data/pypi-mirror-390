"""
Ground Symbol Examples

This file demonstrates various ground symbol configurations and usage patterns.
"""

from jitx.circuit import Circuit
from jitx.design import Design
from jitx.net import Net
from jitx.sample import SampleBoard, SampleSubstrate
from jitxlib.symbols.net_symbols.ground import GroundSymbol, GroundConfig
from jitxlib.symbols.net_symbols.power import PowerConfig, PowerSymbol, SupplySymbol
from jitxlib.symbols.resistor.resistor import ResistorSymbol
from .resistor import ResistorComponent


class NetSymbolCircuit(Circuit):
    """Test circuit with various ground symbols"""

    def __init__(self):
        self.rs = [ResistorComponent(ResistorSymbol()) for _ in range(8)]
        self.nets = [
            [
                Net([self.rs[i].p[1]], name=f"GND[{i}]"),
                Net([self.rs[i].p[2]], name=f"PWR[{i}]"),
            ]
            for i in range(len(self.rs))
        ]

        # Default ground symbol
        self.nets[0][0].symbol = GroundSymbol()
        self.nets[0][1].symbol = PowerSymbol()

        # Custom line width
        self.nets[1][0].symbol = GroundSymbol(line_width=0.1)
        self.nets[1][1].symbol = PowerSymbol(line_width=0.1)

        # Custom porch width
        self.nets[2][0].symbol = GroundSymbol(porch_width=2.0)
        # SupplySymbol can be used interchangeably with PowerSymbol
        self.nets[2][1].symbol = SupplySymbol(porch_width=2.0)

        # Custom spacing
        self.nets[3][0].symbol = GroundSymbol(spacing=0.7)
        self.nets[3][1].symbol = SupplySymbol(bar_width=5.0)

        # Custom line lengths
        self.nets[4][0].symbol = GroundSymbol(max_len=2.0, min_len=0.1, line_count=4)

        # Minimal ground (single line)
        self.nets[5][0].symbol = GroundSymbol(max_len=1.0, min_len=1.0, line_count=1)

        # Wide ground with many lines
        self.nets[6][0].symbol = GroundSymbol(
            max_len=1.5, min_len=0.1, line_count=6, spacing=0.15
        )

        # Custom config object
        custom_ground_config = GroundConfig(
            line_width=0.08,
            porch_width=0.6,
            spacing=0.25,
            max_len=1.4,
            min_len=0.2,
            line_count=4,
        )
        self.nets[7][0].symbol = GroundSymbol(config=custom_ground_config)

        custom_power_config = PowerConfig(
            line_width=0.2,
            porch_width=4.0,
            bar_width=0.5,
        )
        self.combined_net = (
            self.nets[4][1] + self.nets[5][1] + self.nets[6][1] + self.nets[7][1]
        )
        self.combined_net.symbol = PowerSymbol(config=custom_power_config)


class NetSymbolDesign(Design):
    board = SampleBoard()
    substrate = SampleSubstrate()

    def __init__(self):
        self.circuit = NetSymbolCircuit()
