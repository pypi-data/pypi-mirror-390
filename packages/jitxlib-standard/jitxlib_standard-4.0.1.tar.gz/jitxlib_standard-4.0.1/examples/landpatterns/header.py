from jitx.circuit import Circuit
from jitx.component import Component
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.leads import THLead
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.generators.header import Header
from jitxlib.symbols.box import BoxSymbol


class HeaderComponent(Component):
    def __init__(self, num_leads: int, num_rows: int):
        self.ports = [Port() for _ in range(num_leads)]
        self.symbol = BoxSymbol()

        pitch = 2.54
        num_cols = num_leads // num_rows
        body_len = num_rows * pitch
        body_width = num_cols * pitch
        body_height = Toleranced.exact(5.0)
        package_body = RectanglePackage(
            width=Toleranced.exact(body_width),
            length=Toleranced.exact(body_len),
            height=body_height,
        )
        self.landpattern = Header(
            num_leads=num_leads,
            num_rows=num_rows,
            pitch=pitch,
            lead=THLead(
                width=Toleranced.exact(0.9),
                length=Toleranced.exact(2.0),
            ),
        ).package_body(package_body)


class MainCircuit(Circuit):
    comps = (
        HeaderComponent(num_leads=8, num_rows=1),
        HeaderComponent(num_leads=16, num_rows=2),
        HeaderComponent(num_leads=20, num_rows=2),
    )


class HeaderTestDesign(SampleDesign):
    circuit = MainCircuit()
