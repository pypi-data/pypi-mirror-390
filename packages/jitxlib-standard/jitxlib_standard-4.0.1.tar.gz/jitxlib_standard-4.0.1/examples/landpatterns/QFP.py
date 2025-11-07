from jitx.component import Component
from jitx.circuit import Circuit
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.shapes.composites import rectangle
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.generators.qfp import QFP, QFPLead
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.landpatterns.leads import LeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.pads import SMDPadConfig, WindowSubdivide
from jitxlib.symbols.box import BoxSymbol


class QFPComponent(Component):
    def __init__(self, density_level: DensityLevel):
        rows_x = 10
        rows_y = 6
        num_pins = 2 * (rows_x + rows_y) + 1
        self.portSet = [Port() for i in range(num_pins)]
        self.symbol = BoxSymbol()

        width = Toleranced(8.5, 0.05)
        length = Toleranced(10.0, 0.05)

        lead_type = QFPLead(length=Toleranced(0.4, 0.05), width=Toleranced(0.25, 0.05))
        self.landpattern = (
            QFP(
                num_rows=(rows_x, rows_y),
            )
            .lead_profile(
                LeadProfile(
                    span=Toleranced(9.0, 0.05),
                    pitch=0.8,
                    type=lead_type,
                ),
                LeadProfile(
                    span=Toleranced(11.0, 0.05),
                    pitch=1.0,
                    type=lead_type,
                ),
            )
            .package_body(RectanglePackage(width, length, height=Toleranced(0.8, 0.05)))
            .thermal_pad(
                rectangle(5.5, 7.75),
                config=SMDPadConfig(paste=WindowSubdivide(padding=0.25)),
            )
            .density_level(density_level)
        )


class MainCircuit(Circuit):
    comps = [QFPComponent(x) for x in list(DensityLevel)]


class QFPTestDesign(SampleDesign):
    circuit = MainCircuit()
