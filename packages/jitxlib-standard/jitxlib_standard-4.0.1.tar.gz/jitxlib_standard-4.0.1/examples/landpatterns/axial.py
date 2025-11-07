from jitx.component import Component
from jitx.circuit import Circuit
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.leads import THLead
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.twopin.axial import (
    AxialMounting,
    AxialTwoPin,
    PolarizedAxialTwoPin,
)

from jitxlib.symbols.box import BoxSymbol


class AxialComponent(Component):
    """Example from Cornell Dublier, 107TTA025M:
    https://www.cde.com/resources/catalogs/TTA.pdf

    25V, 100uF -  6.3 x 13 mm Cylinder
    8mm Diameter Package x 11.5mm length
    """

    ports = Port(), Port()
    symbol = BoxSymbol()

    def __init__(self, polarized: bool, mounting: AxialMounting):
        lead = THLead(
            length=Toleranced.exact(35.0),
            width=Toleranced.exact(0.5),
        )
        package_body = RectanglePackage(
            length=Toleranced(13.0, 1.5, 0.0),
            width=Toleranced(6.3, 0.5, 0.0),
            height=Toleranced(6.3, 0.5, 0.0),
        )
        if polarized:
            self.landpattern = PolarizedAxialTwoPin(
                lead=lead, package_body=package_body, mounting=mounting
            )
        else:
            self.landpattern = AxialTwoPin(
                lead=lead, package_body=package_body, mounting=mounting
            )


class MainCircuit(Circuit):
    h_unpol = AxialComponent(polarized=False, mounting=AxialMounting.Horizontal)
    h_pol = AxialComponent(polarized=True, mounting=AxialMounting.Horizontal)
    v_unpol = AxialComponent(polarized=False, mounting=AxialMounting.Vertical)
    v_pol = AxialComponent(polarized=True, mounting=AxialMounting.Vertical)


class AxialTestDesign(SampleDesign):
    circuit = MainCircuit()
