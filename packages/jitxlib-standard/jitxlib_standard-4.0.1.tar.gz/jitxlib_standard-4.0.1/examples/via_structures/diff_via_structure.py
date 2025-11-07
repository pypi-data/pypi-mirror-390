# Example of Differential Pair Via Structure

from dataclasses import replace

from jitx.circuit import Circuit
from jitx.component import Component
from jitx.copper import Pour
from jitx.layerindex import LayerSet
from jitx.net import DiffPair, Port, provide
from jitx.sample import SampleDesign, SampleStackup, SampleSubstrate
from jitx.shapes.composites import double_notch_rectangle
from jitx.shapes.primitive import Circle
from jitx.si import (
    ConstrainDiffPair,
    DifferentialRoutingStructure,
    RoutingStructure,
    Topology,
)
from jitx.toleranced import Toleranced
from jitx.units import ohm

from jitxlib.landpatterns.generators.soic import SOIC, SOIC_DEFAULT_LEAD_PROFILE
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.physics import phase_velocity
from jitxlib.symbols.box import BoxSymbol
from jitxlib.via_structures import (
    DifferentialViaStructure,
    PolarViaGroundCage,
    SimpleAntiPad,
)


class SOICComponent(Component):
    def __init__(self, numPins, density_level: DensityLevel):
        self.portSet = [Port() for _ in range(numPins)]
        self.symbol = BoxSymbol()

        self.landpattern = (
            SOIC(num_leads=numPins)
            .narrow(
                Toleranced(
                    (((numPins // 2) - 1) * SOIC_DEFAULT_LEAD_PROFILE.pitch) + 0.7, 0.1
                ),
            )
            .density_level(density_level)
            .lead_profile(
                replace(SOIC_DEFAULT_LEAD_PROFILE, span=Toleranced.min_max(5.8, 6.2)),
            )
        )


vel = phase_velocity(3.6)
outer = RoutingStructure.Layer(
    trace_width=0.15, clearance=0.2, velocity=vel, insertion_loss=0.05
)
inner = RoutingStructure.Layer(
    trace_width=0.125, clearance=0.2, velocity=vel, insertion_loss=0.05
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


outerDP = DifferentialRoutingStructure.Layer(
    trace_width=0.15,
    clearance=0.19,
    velocity=vel,
    insertion_loss=0.05,
    pair_spacing=0.2,
)
innerDP = DifferentialRoutingStructure.Layer(
    trace_width=0.125,
    clearance=0.19,
    velocity=vel,
    insertion_loss=0.05,
    pair_spacing=0.15,
)


DP100 = DifferentialRoutingStructure(
    impedance=100 * ohm,
    uncoupled_region=SE50,
    layers={
        0: outerDP,
        1: innerDP,
        2: innerDP,
        3: innerDP,
        4: innerDP,
        5: outerDP,
    },
)
"""Arbitrary routing structure for a "100 Ohm" differential pair routing
structure for demonstrating topologies with the via structures.
"""


class MainCircuit(Circuit):
    comp1 = SOICComponent(16, DensityLevel.A)
    comp2 = SOICComponent(16, DensityLevel.A)

    @provide.one_of(DiffPair)
    def swappable_pn_1(self, b: DiffPair):
        P, N = self.comp1.portSet[0], self.comp1.portSet[1]
        return [
            {b.p: P, b.n: N},
            {b.p: N, b.n: P},
        ]

    @provide.one_of(DiffPair)
    def swappable_pn_2(self, b: DiffPair):
        P, N = self.comp2.portSet[0], self.comp2.portSet[1]
        return [
            {b.p: P, b.n: N},
            {b.p: N, b.n: P},
        ]

    diffvia = DifferentialViaStructure(
        SampleSubstrate.MicroVia,
        pitch=0.8,
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
                double_notch_rectangle(1.5, 0.85, 0.45, 0.15),
                LayerSet.range(start=0, through=3),
            )
        ],
        insertion_points=DifferentialViaStructure.create_std_insertion_points(0.4),
    )

    def __init__(self):
        self.nets = []

        pt1 = self.require(DiffPair)
        pt2 = self.require(DiffPair)

        self.topos = []
        self.topos.append(pt1 >> self.diffvia.sig_in)
        self.topos.append(self.diffvia.sig_out >> pt2)

        self.dpCst = (
            ConstrainDiffPair(Topology(pt1, pt2))
            .structure(DP100)
            .timing_difference(Toleranced(0.0, 1.0e-12))
        )

        GND = self.diffvia.COMMON + self.comp1.portSet[7] + self.comp2.portSet[7]
        self.nets.append(GND)

        self.topPour = Pour(Circle(diameter=100.0), 0, isolate=0.25, rank=1)
        self.midPour = Pour(Circle(diameter=100.0), 2, isolate=0.25, rank=1)
        GND += self.topPour
        GND += self.midPour


class SixLayerSubstrate(SampleSubstrate):
    stackup = SampleStackup(6)


class DifferentialViaStructureTestDesign(SampleDesign):
    substrate = SixLayerSubstrate()
    circuit = MainCircuit()
