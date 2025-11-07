from jitx.circuit import Circuit
from jitx.component import Component
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.leads import THLead
from jitxlib.landpatterns.package import CylinderPackage
from jitxlib.landpatterns.twopin.radial import PolarizedRadialTwoPin, RadialTwoPin
from jitxlib.symbols.box import BoxSymbol


class RadialComponent(Component):
    def __init__(self, polarized: bool = False):
        self.ports = Port(), Port()
        self.symbol = BoxSymbol()

        lead_spacing = Toleranced(5.0, 0.05)
        lead = THLead(
            length=Toleranced.exact(14),
            width=Toleranced(0.6, 0.05),
        )
        package_body = CylinderPackage(
            diameter=Toleranced(10.0, 0.5),
            height=Toleranced(16.0, 1.0),
        )

        cls = RadialTwoPin if not polarized else PolarizedRadialTwoPin
        self.landpattern = cls(
            lead_spacing=lead_spacing,
            lead=lead,
        ).package_body(package_body)


class MainCircuit(Circuit):
    comp = RadialComponent()
    pol = RadialComponent(polarized=True)


class RadialTestDesign(SampleDesign):
    circuit = MainCircuit()
