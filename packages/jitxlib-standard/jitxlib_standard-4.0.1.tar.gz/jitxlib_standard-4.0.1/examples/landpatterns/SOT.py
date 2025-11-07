from enum import Enum

from jitx.component import Component
from jitx.circuit import Circuit
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.generators.sot import (
    SOT23_3,
    SOT23_5,
    SOT23_6,
    SOTLead,
    SOT_DEFAULT_PITCH,
)
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.landpatterns.leads import LeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.symbols.box import BoxSymbol


class SOT23Type(Enum):
    """SOT-23 Package Type"""

    SOT23_3 = "SOT23-3"
    SOT23_5 = "SOT23-5"
    SOT23_6 = "SOT23-6"


def num_pins(sot_type: SOT23Type) -> int:
    """Number of Pins for a SOT-23 Package Type"""
    match sot_type:
        case SOT23Type.SOT23_3:
            return 3
        case SOT23Type.SOT23_5:
            return 5
        case SOT23Type.SOT23_6:
            return 6
        case _:
            raise ValueError(f"Invalid SOT-23 Package Type: {sot_type}")


def sot_generator(sot_type: SOT23Type) -> type[SOT23_3 | SOT23_5 | SOT23_6]:
    """SOT-23 LandPattern Generator"""
    match sot_type:
        case SOT23Type.SOT23_3:
            return SOT23_3
        case SOT23Type.SOT23_5:
            return SOT23_5
        case SOT23Type.SOT23_6:
            return SOT23_6
        case _:
            raise ValueError(f"Invalid SOT-23 Package Type: {sot_type}")


class SOTComponent(Component):
    def __init__(self, density_level: DensityLevel, sot_type: SOT23Type):
        pin_count = num_pins(sot_type)

        self.portSet = [Port() for i in range(pin_count)]
        self.symbol = BoxSymbol()

        self.landpattern = (
            sot_generator(sot_type)()
            .lead_profile(
                LeadProfile(
                    span=Toleranced.min_max(2.6, 3.0),
                    pitch=SOT_DEFAULT_PITCH,
                    type=SOTLead(
                        length=Toleranced.min_max(0.3, 0.6),
                        width=Toleranced.min_max(0.3, 0.5),
                    ),
                )
            )
            .package_body(
                RectanglePackage(
                    width=Toleranced.min_max(1.45, 1.75),
                    length=Toleranced.min_max(2.75, 3.05),
                    height=Toleranced.min_max(0.9, 1.45),
                )
            )
            .density_level(density_level)
        )


class MainCircuit(Circuit):
    comps = [SOTComponent(d, t) for t in SOT23Type for d in list(DensityLevel)]


class SOTTestDesign(SampleDesign):
    circuit = MainCircuit()
