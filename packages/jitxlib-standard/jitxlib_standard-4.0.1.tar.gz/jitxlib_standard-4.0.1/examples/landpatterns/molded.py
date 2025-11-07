from jitx.circuit import Circuit
from jitx.component import Component
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.keepout import IntraKeepoutGenerator
from jitxlib.landpatterns.leads import SMDLead
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.twopin.molded import (
    MoldedTwoPin,
    PolarizedMoldedTwoPin,
    MOLDED_DEFAULT_PROTRUSION,
)
from jitxlib.symbols.box import BoxSymbol


class MoldedInductor(Component):
    def __init__(self):
        self.ports = Port(), Port()
        self.symbol = BoxSymbol()

        self.landpattern = (
            MoldedTwoPin(
                lead_span=Toleranced(4.9, 0.2),
                lead=SMDLead(
                    width=Toleranced(3.8, 0.1),
                    length=Toleranced(1.2, 0.2),
                    lead_type=MOLDED_DEFAULT_PROTRUSION,
                ),
            )
            .package_body(
                RectanglePackage(
                    length=Toleranced(4.9, 0.2),
                    width=Toleranced(4.9, 0.2),
                    height=Toleranced(4.1, 0.1),
                )
            )
            .keepout(IntraKeepoutGenerator(horizontal=True))
        )


class MoldedCapacitor(Component):
    a = Port()
    c = Port()

    def __init__(self):
        self.symbol = BoxSymbol()

        self.landpattern = PolarizedMoldedTwoPin(
            lead_span=Toleranced(5.8, 0.2),
            lead=SMDLead(
                width=Toleranced(2.2, 0.2),
                length=Toleranced(1.3, 0.3),
                lead_type=MOLDED_DEFAULT_PROTRUSION,
            ),
        ).package_body(
            RectanglePackage(
                length=Toleranced(5.8, 0.2),
                width=Toleranced(3.2, 0.2),
                height=Toleranced(2.5, 0.2),
            )
        )


class MainCircuit(Circuit):
    comps = MoldedInductor(), MoldedCapacitor()


class MoldedTestDesign(SampleDesign):
    circuit = MainCircuit()
