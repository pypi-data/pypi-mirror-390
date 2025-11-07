from jitx.component import Component
from jitx.circuit import Circuit
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.shapes.composites import rectangle
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.generators.qfn import QFN, QFNLead
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.landpatterns.leads import LeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.pads import SMDPadConfig, WindowSubdivide
from jitxlib.symbols.box import BoxSymbol


class QFNComponent(Component):
    def __init__(self, numPins: int, density_level: DensityLevel):
        self.portSet = [Port() for i in range(numPins + 1)]
        self.symbol = BoxSymbol()

        width = Toleranced(5.0, 0.05)
        height = Toleranced(0.8, 0.05)
        pitch = 0.5
        lead_length = Toleranced(0.4, 0.05)
        lead_width = Toleranced(0.25, 0.05)
        package_body = RectanglePackage(width=width, length=width, height=height)
        self.landpattern = (
            QFN(num_leads=numPins)
            .package_body(package_body)
            .density_level(density_level)
            .thermal_pad(
                shape=rectangle(3.7, 3.7),
                config=SMDPadConfig(paste=WindowSubdivide(padding=0.25)),
            )
            .lead_profile(LeadProfile(width, pitch, QFNLead(lead_length, lead_width)))
        )


class MainCircuit(Circuit):
    comps = [QFNComponent(32, x) for x in list(DensityLevel)]


class QFNTestDesign(SampleDesign):
    circuit = MainCircuit()
