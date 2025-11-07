from jitx.sample import SampleDesign
from jitx.circuit import Circuit
from jitx.component import Component
from jitx.net import Port
from jitx.toleranced import Toleranced
from jitx.shapes.composites import rectangle

from jitxlib.landpatterns.courtyard import ExcessCourtyard, OriginMarkerMixin
from jitxlib.landpatterns.pads import RelAdj, SMDPadConfig
from jitxlib.landpatterns.generators.bga import BGABase
from jitxlib.landpatterns.generators.qfn import QFNBase, QFNLead
from jitxlib.landpatterns.grid_layout import AlphaDictNumbering, LinearNumbering
from jitxlib.landpatterns.grid_planner import (
    CompositeGridPlanner,
    CornerCutGridPlanner,
    InactiveIslandGridPlanner,
)
from jitxlib.landpatterns.ipc import DensityLevel, DensityLevelContext
from jitxlib.landpatterns.leads import LeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.pads import WindowSubdivide
from jitxlib.landpatterns.silkscreen.marker import Pad1Marker
from jitxlib.landpatterns.silkscreen.outlines import SilkscreenOutline, SoldermaskBased
from jitxlib.symbols.box import BoxSymbol


class QFNPadsWithThermal(LinearNumbering, QFNBase):
    def __init__(self, num_qfn_leads: int):
        super().__init__(num_rows=num_qfn_leads // 4)

    def __base_init__(self):
        super().__base_init__()
        self.lead_profile(
            LeadProfile(
                span=Toleranced(5.0, 0.05),
                pitch=0.5,
                type=QFNLead(
                    length=Toleranced(0.4, 0.05),
                    width=Toleranced(0.25, 0.05),
                ),
            )
        )
        self.thermal_pad(
            rectangle(3.7, 3.7), SMDPadConfig(paste=WindowSubdivide(padding=0.25))
        )


class BGAPads(AlphaDictNumbering, BGABase):
    pass


class PackageLandpattern(
    Pad1Marker, SilkscreenOutline, OriginMarkerMixin, ExcessCourtyard
):
    pass


class BGAQFNComponent(Component):
    density_level = DensityLevelContext(DensityLevel.A)

    def __init__(self):
        num_qfn_leads = 24
        num_qfn_pads = num_qfn_leads + 1

        bga_rows = 6
        bga_cols = 6
        bga_grid_planner = CompositeGridPlanner(
            CornerCutGridPlanner(1),
            InactiveIslandGridPlanner(3, 4, 3, 4),
        )
        num_bga_pads = bga_grid_planner.num_active(bga_rows, bga_cols)

        num_ports = num_qfn_pads + num_bga_pads

        self.portSet = [Port() for i in range(num_ports)]
        self.symbol = BoxSymbol()

        pkg_body = RectanglePackage(
            width=Toleranced(13.0, 0.05),
            length=Toleranced(13.0, 0.05),
            height=Toleranced(0.8, 0.05),
        )

        self.qfn = QFNPadsWithThermal(num_qfn_leads).at(0.0, 4.0)

        self.bga = (
            BGAPads(
                num_rows=bga_rows,
                num_cols=bga_cols,
                ball_diameter=1.0,
                pitch=1.27,
            )
            .pad_config(
                SMDPadConfig(
                    copper=RelAdj(-0.1),
                    soldermask=RelAdj(-0.05),
                ),
            )
            .grid_planner(
                bga_grid_planner,
            )
            .at(0.0, -4.0)
        )

        self.surround = (
            PackageLandpattern()
            .package_body(pkg_body)
            .apply_to(self.qfn, self.bga)
            .silkscreen_outline(SoldermaskBased())
            .pad_1_marker_direction(None, margin=0.2)
        )


class MainCircuit(Circuit):
    bga = BGAQFNComponent()


class BGAQFNTestDesign(SampleDesign):
    circuit = MainCircuit()
