from jitx.circuit import Circuit
from jitx.component import Component
from jitx.container import inline
from jitx.net import Port
from jitx.sample import SampleDesign
from jitx.toleranced import Toleranced

from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.landpatterns.generators.bga import BGA
from jitxlib.landpatterns.grid_planner import (
    CompositeGridPlanner,
    CornerCutGridPlanner,
    InactiveIslandGridPlanner,
    StaggeredGridPlanner,
)
from jitxlib.landpatterns.pads import RelAdj, THPadConfig
from jitxlib.symbols.box import BoxSymbol


class BGAComponent(Component):
    def __init__(self):
        grid_planner = CompositeGridPlanner(
            CornerCutGridPlanner(4),
            InactiveIslandGridPlanner(10, 12, 10, 12),
            StaggeredGridPlanner(),
        )
        num_rows = 21
        num_cols = 21
        num_pads = grid_planner.num_active(num_rows, num_cols)

        pitch = 1.27
        pkg_body = RectanglePackage(
            width=Toleranced(13.0, 0.05),
            length=Toleranced(13.0, 0.05),
            height=Toleranced(0.8, 0.05),
        )

        self.portSet = [Port() for i in range(num_pads)]
        self.symbol = BoxSymbol()
        self.landpattern = (
            BGA(
                num_rows=num_rows,
                num_cols=num_cols,
                pitch=pitch,
                ball_diameter=1.0,
            )
            .grid_planner(grid_planner)
            .pad_config(
                THPadConfig(
                    copper=RelAdj(-0.1),
                    cutout=RelAdj(-0.25),
                    soldermask=RelAdj(-0.05),
                    paste=RelAdj(-0.1),
                )
            )
            .package_body(pkg_body)
        )


class BGATestDesign(SampleDesign):
    @inline
    class circuit(Circuit):
        comp = BGAComponent().at(0, 0)
