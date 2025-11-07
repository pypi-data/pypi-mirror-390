from jitx.component import Component
from jitx.circuit import Circuit
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.generators.soic import SOIC, SOIC_DEFAULT_LEAD_PROFILE
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.symbols.box import BoxSymbol


class SOICComponent(Component):
    def __init__(self, numPins, density_level: DensityLevel):
        self.portSet = [Port() for i in range(numPins)]
        self.symbol = BoxSymbol()

        self.landpattern = (
            SOIC(num_leads=numPins)
            .narrow(
                package_length=Toleranced(
                    (((numPins // 2) - 1) * SOIC_DEFAULT_LEAD_PROFILE.pitch) + 0.7, 0.1
                ),
                span=Toleranced.min_max(5.8, 6.2),
            )
            .density_level(density_level)
        )


class MainCircuit(Circuit):
    comp8 = [SOICComponent(8, x) for x in list(DensityLevel)]
    comp16 = [SOICComponent(16, x) for x in list(DensityLevel)]


class SOICTestDesign(SampleDesign):
    circuit = MainCircuit()
