from jitx.component import Component
from jitx.circuit import Circuit
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.shapes.composites import rectangle
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.generators.sop import SOP, SOPLead
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.landpatterns.leads import LeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.pads import SMDPadConfig, WindowSubdivide
from jitxlib.symbols.box import BoxSymbol


class SOPComponent(Component):
    def __init__(self, num_pins: int, density_level: DensityLevel):
        self.portSet = [Port() for i in range(num_pins + 1)]
        self.symbol = BoxSymbol()

        pitch = 0.65
        pkg_len = (((num_pins / 2) - 1) * pitch) + 1.1
        package_body = RectanglePackage(
            width=Toleranced.min_max(4.3, 4.5),
            length=Toleranced(pkg_len, 0.1),
            height=Toleranced.min_max(1.0, 1.2),
        )

        self.landpattern = (
            SOP(
                num_leads=num_pins,
            )
            .lead_profile(
                LeadProfile(
                    span=Toleranced.min_max(6.2, 6.6),
                    pitch=pitch,
                    type=SOPLead(
                        length=Toleranced.min_max(0.5, 0.75),
                        width=Toleranced.min_max(0.19, 0.3),
                    ),
                ),
            )
            .package_body(package_body)
            .thermal_pad(
                rectangle(3.155, 3.255),
                SMDPadConfig(paste=WindowSubdivide(padding=0.25)),
            )
            .density_level(density_level)
        )


class MainCircuit(Circuit):
    comps14 = [SOPComponent(14, x) for x in list(DensityLevel)]
    comps20 = [SOPComponent(20, x) for x in list(DensityLevel)]


class SOPTestDesign(SampleDesign):
    circuit = MainCircuit()
