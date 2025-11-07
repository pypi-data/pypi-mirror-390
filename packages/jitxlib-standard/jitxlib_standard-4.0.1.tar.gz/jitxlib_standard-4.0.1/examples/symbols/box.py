"""
Test module for box symbols functionality.

This module contains comprehensive tests for the box symbol implementations.
"""

# Import JITX components for the design
from jitx.common import DiffPair
from jitx.inspect import extract
import jitx.test
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.landpattern import Landpattern, Pad
from jitx.net import Port
from jitx.design import Design
from jitx.shapes.primitive import Polygon

# Import our custom box symbol
from jitxlib.symbols.context import SymbolStyleContext
from jitxlib.symbols.box import BoxConfig, BoxSymbol, Column, PinGroup, Row
from jitxlib.symbols.decorators import (
    ActiveLow,
    Bidirectional,
    Clock,
    Input,
    OpenCollectorSink,
    OpenCollectorSource,
    Output,
    decorate,
)
from jitxlib.symbols.label import LabelConfig

from examples.defaults.board import DefaultBoard, DefaultSubstrate


class SamplePad(Pad):
    shape = Polygon([(-0.3, -0.4), (0.3, -0.4), (0.3, 0.4), (-0.3, 0.4)])


class SampleLandpattern(Landpattern):
    def __init__(self, num_ports: int, start_pad_id: int = 0):
        # Create a pad for each port
        self.p = {}
        for i in range(start_pad_id, start_pad_id + num_ports):
            self.p[i] = SamplePad().at(i, 0.0)


class BaseComponent(Component):
    mpn = "BOX"
    manufacturer = "Test Co"
    reference_designator_prefix = "B"


class EmptyComponent(BaseComponent):
    def __init__(self):
        super().__init__()
        self.landpattern = SampleLandpattern(0)


class BoxComponentEmpty(EmptyComponent):
    def __init__(self):
        super().__init__()
        self.symbol = BoxSymbol(debug=True)


class BoxComponentEmptyArgs(EmptyComponent):
    symbol = BoxSymbol()

    def __init__(self):
        super().__init__()


class SinglePinBoxComponent(BaseComponent):
    A = Port()

    def __init__(self):
        super().__init__()
        decorate(self.A, Clock(3.0))
        self.landpattern = SampleLandpattern(1)
        self.symbol = BoxSymbol(
            columns=Column(up=PinGroup(self.A)),
            debug=True,
        )


class BaseBoxComponent(BaseComponent):
    IN = [Port() for _ in range(10)]
    OUT = [Port() for _ in range(8)]
    GND = [Port() for _ in range(2)]
    VCC = [Port() for _ in range(2)]
    CLK = Port()
    RST = Port()
    EN = [Port() for _ in range(2)]

    def __init__(self):
        super().__init__()
        decorators = [
            Input(),
            Output(),
            Bidirectional(),
            OpenCollectorSource(),
            OpenCollectorSink(),
            ActiveLow(),
            Clock(),
        ]

        for i, port in enumerate(extract(self, Port)):
            decorate(port, decorators[i % len(decorators)])

        self.landpattern = SampleLandpattern(len(tuple(extract(self, Port))))


class BaseBundleBoxComponent(BaseComponent):
    A = DiffPair()
    B = [DiffPair(), DiffPair()]
    C = [DiffPair(), DiffPair(), DiffPair()]


class BoxComponent1(BaseBoxComponent):
    def __init__(self):
        super().__init__()
        self.symbol = BoxSymbol(
            rows=[
                Row(
                    left=PinGroup(self.IN),
                    right=PinGroup(self.OUT),
                )
            ],
            columns=[
                Column(
                    up=PinGroup(self.EN, self.CLK, self.RST),
                    down=PinGroup(self.GND + self.VCC),
                )
            ],
            debug=True,
        )


class BoxComponent2(BaseBoxComponent):
    def __init__(self):
        super().__init__()
        self.symbol = BoxSymbol(
            rows=[
                Row(
                    left=[PinGroup(self.IN[:5]), PinGroup(self.IN[5:])],
                    right=[PinGroup(self.OUT[:4]), PinGroup(self.OUT[4:])],
                )
            ],
            columns=[
                Column(
                    up=[PinGroup([self.CLK, self.RST]), PinGroup(self.EN)],
                    down=[PinGroup(self.GND), PinGroup(self.VCC)],
                )
            ],
            debug=True,
        )


class BoxComponent3(BaseBoxComponent):
    def __init__(self):
        super().__init__()
        self.symbol = BoxSymbol(
            rows=[
                Row(
                    left=[
                        PinGroup(self.IN[:5], pre_margin=1),
                        PinGroup(self.IN[5:], pre_margin=2),
                    ],
                    right=[
                        PinGroup(self.OUT[:4], pre_margin=1),
                        PinGroup(self.OUT[4:], pre_margin=2),
                    ],
                )
            ],
            columns=[
                Column(
                    up=[
                        PinGroup([self.CLK, self.RST], pre_margin=3),
                        PinGroup(self.EN, pre_margin=4),
                    ],
                    down=[
                        PinGroup(self.GND, pre_margin=5),
                        PinGroup(self.VCC, pre_margin=6),
                    ],
                )
            ],
            debug=True,
        )


class BoxComponent4(BaseBoxComponent):
    def __init__(self):
        super().__init__()
        self.symbol = BoxSymbol(
            rows=[
                Row(
                    left=[
                        PinGroup([self.CLK, self.RST]),
                        PinGroup(self.EN),
                    ],
                    right=[
                        PinGroup(self.OUT[:2]),
                        PinGroup(self.OUT[2:5]),
                    ],
                ),
                Row(
                    left=[
                        PinGroup(self.IN[:5]),
                    ],
                    right=[
                        PinGroup(self.OUT[5:]),
                    ],
                ),
                Row(
                    left=[
                        PinGroup(self.IN[5:]),
                    ],
                    right=[
                        PinGroup(self.GND + self.VCC),
                    ],
                ),
            ],
            debug=True,
            config=BoxConfig(
                min_width=10.0,
                group_spacing=2,
            ),
        )


class BoxComponent5(BaseBoxComponent):
    def __init__(self):
        super().__init__()
        self.symbol = BoxSymbol(
            rows=[
                Row(
                    left=[
                        PinGroup([self.CLK, self.RST], pre_margin=1),
                        PinGroup(self.EN, pre_margin=3),
                    ],
                    right=[
                        PinGroup(self.OUT[:2], pre_margin=2),
                        PinGroup(self.OUT[2:5], pre_margin=3),
                    ],
                    top_margin=5,
                    bottom_margin=5,
                ),
                Row(
                    right=[
                        PinGroup(self.OUT[5:], post_margin=5),
                    ],
                    top_margin=5,
                    bottom_margin=5,
                ),
            ],
            columns=[
                Column(
                    up=[
                        PinGroup(self.IN[:4], pre_margin=3),
                        PinGroup(self.IN[4:8], pre_margin=4),
                    ],
                    down=[
                        PinGroup(self.GND, pre_margin=4),
                        PinGroup(self.VCC, pre_margin=2),
                    ],
                    left_margin=5,
                    right_margin=5,
                ),
                Column(
                    up=[
                        PinGroup(self.IN[8:], pre_margin=6),
                    ],
                    left_margin=5,
                    right_margin=5,
                ),
            ],
            debug=True,
            config=BoxConfig(
                min_width=2.0,
                min_height=2.0,
                pin_spacing=2.0,
                corner_margin=4.0,
                group_spacing=2.0,
                row_spacing=4.0,
                col_spacing=4.0,
            ),
        )


class AutoBoxComponent(Component):
    mpn = "AUTOBOX"
    manufacturer = "Test Co"
    reference_designator_prefix = "B"

    def __init__(self):
        self.P = {
            "A": [Port() for _ in range(1)],
            "B": [Port() for _ in range(2)],
            "C": [Port() for _ in range(3)],
            "D": [Port() for _ in range(4)],
            "E": [Port() for _ in range(5)],
            "F": [Port() for _ in range(6)],
            "G": [Port() for _ in range(7)],
            "H": [Port() for _ in range(8)],
            "I": [Port() for _ in range(9)],
            "J": [Port() for _ in range(10)],
        }

        self.landpattern = SampleLandpattern(num_ports=len(list(extract(self, Port))))
        self.symbol = BoxSymbol(debug=False)


class BundleBoxComponent1(BaseBundleBoxComponent):
    def __init__(self):
        super().__init__()
        self.landpattern = SampleLandpattern(num_ports=len(list(extract(self, Port))))
        self.symbol = BoxSymbol(
            rows=Row(
                left=PinGroup(self.C, self.A),
                right=PinGroup(self.B),
            ),
        )


class BundleBoxComponent2(BaseBundleBoxComponent):
    def __init__(self):
        super().__init__()
        self.landpattern = SampleLandpattern(num_ports=len(list(extract(self, Port))))
        self.symbol = BoxSymbol()


class BoxCircuit(Circuit):
    def __init__(self):
        self.empty1 = BoxComponentEmpty()
        self.empty2 = BoxComponentEmptyArgs()
        self.c0 = SinglePinBoxComponent()
        self.c1 = BoxComponent1()
        self.c2 = BoxComponent2()
        self.c3 = BoxComponent3()
        self.c4 = BoxComponent4()
        self.c5 = BoxComponent5()
        self.abc1 = AutoBoxComponent()
        self.mbc1 = BundleBoxComponent1()
        self.mbc2 = BundleBoxComponent2()


class BoxDesign(Design):
    board = DefaultBoard()
    substrate = DefaultSubstrate()
    symbol_style_context = SymbolStyleContext(
        box_config=BoxConfig(
            min_width=2.0,
            min_height=2.0,
            pin_spacing=1.0,
            corner_margin=2.0,
            group_spacing=2.0,
            row_spacing=2.0,
            col_spacing=2.0,
        ),
        label_config=LabelConfig(ref_size=1.0, value_size=1.0),
    )

    def __init__(self):
        self.circuit = BoxCircuit()


class BoxSymbolTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = BoxDesign()

        import jitx._translate.design

        jitx._translate.design.package_design(design)
