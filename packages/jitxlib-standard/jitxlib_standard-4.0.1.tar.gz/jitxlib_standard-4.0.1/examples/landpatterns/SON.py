from jitx.component import Component
from jitx.circuit import Circuit
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.shapes.composites import rectangle
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.generators.son import SON, SONLead
from jitxlib.landpatterns.leads import LeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.pads import SMDPadConfig, WindowSubdivide
from jitxlib.symbols.box import BoxSymbol


class SONComponent(Component):
    def __init__(self):
        num_pins = 8
        self.portSet = [Port() for i in range(num_pins + 1)]
        self.symbol = BoxSymbol()

        pitch = 0.5
        pkg_len = (((num_pins / 2) - 1) * pitch) + 0.5
        package_body = RectanglePackage(
            width=Toleranced.min_max(1.9, 2.1),
            length=Toleranced(pkg_len, 0.1),
            height=Toleranced.min_max(0.7, 0.8),
        )

        self.landpattern = (
            SON(
                num_leads=num_pins,
            )
            .lead_profile(
                LeadProfile(
                    span=Toleranced.min_max(1.9, 2.1),
                    pitch=pitch,
                    type=SONLead(
                        length=Toleranced.min_max(0.2, 0.4),
                        width=Toleranced.min_max(0.18, 0.32),
                    ),
                ),
            )
            .package_body(package_body)
            .thermal_pad(
                rectangle(0.9, 1.6),
                SMDPadConfig(paste=WindowSubdivide(padding=0.25)),
            )
        )


class MainCircuit(Circuit):
    comps = SONComponent()


class SONTestDesign(SampleDesign):
    circuit = MainCircuit()
