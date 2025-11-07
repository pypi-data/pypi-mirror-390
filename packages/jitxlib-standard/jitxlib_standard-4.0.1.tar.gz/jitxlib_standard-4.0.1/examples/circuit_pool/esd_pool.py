from itertools import chain
from jitx.component import Component
from jitx.common import PassThrough, DualPair
from jitx.circuit import Circuit
from jitx.landpattern import PadMapping
from jitx.net import Port, provide, Provide, DiffPair
from jitx.si import BridgingPinModel
from jitx.design import Design
from jitx.toleranced import Toleranced
from jitxlib.circuits.pool import CircuitPool


from jitxlib.landpatterns.generators.soic import SOIC, SOIC_DEFAULT_LEAD_PROFILE
from jitxlib.landpatterns.ipc import DensityLevel, DensityLevelContext
from jitxlib.symbols.box import BoxSymbol, Row, PinGroup

from examples.defaults.board import DefaultBoard, DefaultSubstrate

import jitx.test


class ESDDevice(Component):
    """Multi-channel ESD protection device.
    This is a mock for something like a TI, ESD224DQAR
    """

    NUM_SE_CHS = 4
    NUM_DP_CHS = NUM_SE_CHS // 2

    IOC = [Port() for i in range(NUM_SE_CHS)]
    IOS = [Port() for i in range(NUM_SE_CHS)]

    GND = Port()

    # For Testing Only
    numPins = 10
    lp = SOIC(num_leads=numPins).narrow(
        package_length=Toleranced(
            (((numPins // 2) - 1) * SOIC_DEFAULT_LEAD_PROFILE.pitch) + 0.7, 0.1
        ),
        span=Toleranced.min_max(5.8, 6.2),
    )

    def __init__(self):
        lp = self.lp

        self.symbol = BoxSymbol(
            rows=[
                Row(
                    left=[PinGroup(self.IOC), PinGroup([self.GND])],
                    right=[PinGroup(self.IOS)],
                )
            ],
        )

        pads = lp.p
        self.padMap = PadMapping(
            chain.from_iterable(
                [
                    [(self.GND, [pads[3], pads[8]])],
                    [
                        (self.IOC[0], pads[1]),
                        (self.IOC[1], pads[2]),
                        (self.IOC[2], pads[4]),
                        (self.IOC[3], pads[5]),
                    ],
                    [
                        (self.IOS[0], pads[10]),
                        (self.IOS[1], pads[9]),
                        (self.IOS[2], pads[7]),
                        (self.IOS[3], pads[6]),
                    ],
                ]
            )
        )

        self.models = [
            BridgingPinModel(self.IOC[i], self.IOS[i], delay=0.0, loss=0.0)
            for i in range(self.NUM_SE_CHS)
        ]


class ESDProtector(Circuit):
    """Circuit Wrapper around the ESD224 that implements the
    provide ports for the single passthroughs and the diff-pairs.
    """

    C = ESDDevice()

    @provide(PassThrough)
    def passthrough_channels(self, bd: PassThrough):
        return [{bd.A: a, bd.B: b} for a, b in zip(self.C.IOC, self.C.IOS, strict=True)]

    @provide(DualPair)
    def diffpair_channels(self, b: DualPair):
        return [
            {
                b.A.p: self.C.IOC[2 * i],
                b.A.n: self.C.IOC[(2 * i) + 1],
                b.B.p: self.C.IOS[2 * i],
                b.B.n: self.C.IOS[(2 * i) + 1],
            }
            for i in range(self.C.NUM_DP_CHS)
        ]


class SOICComponent(Component):
    @provide(DiffPair)
    def diffpair_channel(self, b: DiffPair):
        return [{b.p: self.portSet[0], b.n: self.portSet[1]}]

    def __init__(self, numPins):
        self.portSet = [Port() for i in range(numPins)]

        self.landpattern = SOIC(num_leads=numPins).narrow(
            package_length=Toleranced(
                (((numPins // 2) - 1) * SOIC_DEFAULT_LEAD_PROFILE.pitch) + 0.7, 0.1
            ),
            span=Toleranced.min_max(5.8, 6.2),
        )

        self.symbol = BoxSymbol(
            rows=[
                Row(
                    left=[PinGroup(self.portSet[: numPins // 2])],
                    right=[PinGroup(self.portSet[numPins // 2 :])],
                )
            ]
        )

        pads = self.landpattern.p
        self.cmappings = [
            PadMapping(
                {self.portSet[i]: pads[i + 1] for i in range(numPins)},
            )
        ]


class MainCircuit(Circuit):
    density_level = DensityLevelContext(DensityLevel.A)

    comp8 = SOICComponent(8)
    comp16 = SOICComponent(16)

    pool = CircuitPool(ESDProtector, 2)

    def __init__(self):
        src = Provide.require(DiffPair, self.comp8)
        dst = Provide.require(DiffPair, self.comp16)

        dpPassthrough = self.pool.require(DualPair)
        self.nets = []
        self.nets.append(src + dpPassthrough.A)
        self.nets.append(dpPassthrough.B + dst)


class CircuitPoolTestDesign(Design):
    substrate = DefaultSubstrate()
    board = DefaultBoard()
    circuit = MainCircuit()


class CircuitPoolTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = CircuitPoolTestDesign()
        self.assertIsInstance(design.circuit, MainCircuit)

        import jitx._translate.design

        jitx._translate.design.package_design(design)
