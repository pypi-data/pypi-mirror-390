# Single-Ended Via Structure Example

from dataclasses import replace

from jitx.circuit import Circuit
from jitx.component import Component
from jitx.copper import Pour
from jitx.layerindex import LayerSet
from jitx.net import Port
from jitx.sample import SampleDesign, SampleStackup, SampleSubstrate
from jitx.shapes.composites import double_chipped_circle
from jitx.shapes.primitive import Circle
from jitx.si import (
    Constrain,
    ConstrainReferenceDifference,
    RoutingStructure,
)
import jitx.test
from jitx.toleranced import Toleranced
from jitx.units import ohm

from jitxlib.landpatterns.generators.soic import SOIC, SOIC_DEFAULT_LEAD_PROFILE
from jitxlib.landpatterns.ipc import DensityLevel, DensityLevelContext
from jitxlib.physics import phase_velocity
from jitxlib.symbols.box import BoxSymbol
from jitxlib.via_structures import PolarViaGroundCage, SimpleAntiPad, SingleViaStructure


class SOICComponent(Component):
    def __init__(self, numPins):
        self.portSet = [Port() for _ in range(numPins)]
        self.symbol = BoxSymbol()

        self.landpattern = (
            SOIC(num_leads=numPins)
            .narrow(
                package_length=Toleranced(
                    (((numPins // 2) - 1) * SOIC_DEFAULT_LEAD_PROFILE.pitch) + 0.7, 0.1
                ),
            )
            .lead_profile(
                replace(SOIC_DEFAULT_LEAD_PROFILE, span=Toleranced.min_max(5.8, 6.2)),
            )
        )


vel = phase_velocity(3.6)
outer = RoutingStructure.Layer(
    trace_width=0.15, clearance=0.2, velocity=vel, insertion_loss=0.05
)
inner = RoutingStructure.Layer(
    trace_width=0.25, clearance=0.2, velocity=vel, insertion_loss=0.05
)


SE50 = RoutingStructure(
    impedance=50 * ohm,
    layers={
        0: outer,
        1: inner,
        2: inner,
        3: inner,
        4: inner,
        5: outer,
    },
)
"""Defines an arbitrary Single-Ended "50 Ohm" routing structure.
This will be used to demonstrate structure constraints on the topology going through
a single-ended via structure.
"""


class MainCircuit(Circuit):
    density_level = DensityLevelContext(DensityLevel.A)
    comp1 = SOICComponent(16)
    comp2 = SOICComponent(16)

    BUS_LEN = 4

    ssvia = [
        SingleViaStructure(
            SampleSubstrate.MicroVia,
            ground_cages=[
                PolarViaGroundCage(
                    SampleSubstrate.THVia,
                    count=12,
                    radius=0.85,
                    skips=[0, 2, 3, 4, 6, 8, 9, 10],
                )
            ],
            antipads=[
                SimpleAntiPad(
                    double_chipped_circle(0.5, 0.4), LayerSet.range(start=0, through=3)
                )
            ],
            insertion_points=SingleViaStructure.create_std_insertion_points(0.8),
        )
        for i in range(BUS_LEN)
    ]

    def __init__(self):
        self.nets = []
        GND = self.comp1.portSet[7] + self.comp2.portSet[7]
        self.nets.append(GND)

        self.topos = []
        EPs = []
        for i in range(self.BUS_LEN):
            # Topology
            self.topos.append(self.comp1.portSet[i] >> self.ssvia[i].sig_in)
            self.topos.append(self.ssvia[i].sig_out >> self.comp2.portSet[i])
            EPs.append(self.comp1.portSet[i].to(self.comp2.portSet[i]))
            GND += self.ssvia[i].COMMON

        # Apply constraints to all of the topos
        self.rc = ConstrainReferenceDifference(
            guide=EPs[0], topologies=EPs[1:]
        ).timing_difference(Toleranced(0.0, 1.0e-12))

        self.sc = Constrain(EPs).structure(SE50)

        self.topPour = Pour(Circle(diameter=100.0), 0, isolate=0.25, rank=1)
        self.midPour = Pour(Circle(diameter=100.0), 2, isolate=0.25, rank=1)
        GND += self.topPour
        GND += self.midPour


class SixLayerSubstrate(SampleSubstrate):
    stackup = SampleStackup(6)


class SingleEndedViaStructureTestDesign(SampleDesign):
    substrate = SixLayerSubstrate()
    circuit = MainCircuit()


class SOICTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = SingleEndedViaStructureTestDesign()
        self.assertIsInstance(design.circuit, MainCircuit)

        import jitx._translate.design

        jitx._translate.design.package_design(design)
