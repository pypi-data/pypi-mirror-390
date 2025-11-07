from jitx.anchor import Anchor
from jitx.circuit import Circuit
from jitx.component import Component
from jitx.container import inline
from jitx.landpattern import PadMapping
from jitx.net import Port
from jitx.sample import SampleDesign, SampleSubstrate
from jitx.shapes.composites import rectangle
from jitx.substrate import SubstrateContext
from jitx.toleranced import Toleranced
import jitx.test
from jitx.units import Mohm

from jitxlib.landpatterns.courtyard import ExcessCourtyard, OriginMarkerMixin
from jitxlib.landpatterns.dual import DualColumn
from jitxlib.landpatterns.generators.bga import BGA
from jitxlib.landpatterns.generators.qfn import QFN, QFNLead
from jitxlib.landpatterns.generators.soic import SOIC
from jitxlib.landpatterns.grid_layout import A1, AlphaDictNumbering, LinearNumbering
from jitxlib.landpatterns.leads import LeadProfile
from jitxlib.landpatterns.leads.protrusions import SmallGullWingLeads
from jitxlib.landpatterns.pads import (
    SMDPadConfig,
    ThermalPadGeneratorMixin,
    WindowSubdivide,
)
from jitxlib.landpatterns.quad import QuadColumn
from jitxlib.landpatterns.silkscreen.labels import (
    ReferenceDesignatorMixin,
    ValueLabelMixin,
)
from jitxlib.landpatterns.silkscreen.marker import Pad1Marker
from jitxlib.landpatterns.silkscreen.outlines import (
    InterstitialOutline,
    SilkscreenLine,
    SilkscreenOutline,
    SoldermaskBased,
    PackageBased,
)
from jitxlib.symbols.box import BoxSymbol


class DualColumnBase(SilkscreenOutline, DualColumn):
    def __base_init__(self):
        super().__base_init__()
        self.pad_config(SMDPadConfig())


class DualColumnLandpattern(
    A1,
    AlphaDictNumbering,
    ReferenceDesignatorMixin,
    ValueLabelMixin,
    OriginMarkerMixin,
    Pad1Marker,
    ExcessCourtyard,
    DualColumnBase,
):
    def __base_init__(self):
        super().__base_init__()
        (
            self.silkscreen_outline(
                SoldermaskBased()
                .silkscreen_line(SilkscreenLine.Vertical, -0.15)
                .silkscreen_corner(0.5)
                .line_width(0.5)
            )
            # .reference_designator(Anchor.NW)
            .value_label()
        )


class DualColumnLinearLandpattern(LinearNumbering, DualColumnBase):
    def __base_init__(self):
        super().__base_init__()
        self.lead_profile(
            pitch=1.27,
            span=3 * 1.27,
            length=1.27,
            width=0.4,
            protrusion=SmallGullWingLeads,
        )


class DualColumnComponent(Component):
    lp = (
        DualColumnLandpattern(num_rows=3)
        .lead_profile(
            pitch=1.27,
            span=4 * 1.27,
            length=1.27,
            width=0.4,
            protrusion=SmallGullWingLeads,
        )
        .silkscreen_outline(InterstitialOutline(vertical=True))
        .pad_1_marker_direction(Anchor.E)
    )

    value = 100 * Mohm

    A = Port(), Port()
    B = Port(), Port()
    C = Port(), Port()

    mapping = PadMapping(
        {
            A[0]: lp.A[1],
            A[1]: lp.A[2],
            B[0]: lp.A[3],
            B[1]: lp.B[1],
            C[0]: lp.B[2],
            C[1]: lp.B[3],
        }
    )

    symbol = BoxSymbol()


class QuadColumnLandpattern(
    # make sure A1 gets applied _before_ column major order from QuadColumn
    A1,
    AlphaDictNumbering,
    Pad1Marker,
    ExcessCourtyard,
    SilkscreenOutline,
    ReferenceDesignatorMixin,
    ThermalPadGeneratorMixin,
    QuadColumn,
):
    def __base_init__(self):
        super().__base_init__()
        self.silkscreen_outline(SoldermaskBased().silkscreen_corner(0.3))
        self.pad_config(SMDPadConfig())
        self.reference_designator(Anchor.NE)
        self.thermal_pad(
            shape=rectangle(4, 4),
            config=SMDPadConfig(paste=WindowSubdivide(padding=0.25, gridShape=(3, 3))),
        )


class WeirdQuadColumnComponent(Component):
    lp = (
        QuadColumnLandpattern(num_rows=(1, 2, 3, 4))
        .lead_profile(
            pitch=1.27,
            span=7 * 1.27,
            length=1.27,
            width=0.4,
            protrusion=SmallGullWingLeads,
        )
        .silkscreen_outline(
            InterstitialOutline().silkscreen_line(SilkscreenLine.Horizontal)
        )
    )

    A = (Port(),)
    B = Port(), Port()
    C = Port(), Port(), Port()
    D = Port(), Port(), Port(), Port()

    mapping = PadMapping(
        {
            A[0]: lp.A[1],
            B[0]: lp.B[1],
            B[1]: lp.B[2],
            C[0]: lp.C[1],
            C[1]: lp.C[2],
            C[2]: lp.C[3],
            D[0]: lp.D[1],
            D[1]: lp.D[2],
            D[2]: lp.D[3],
            D[3]: lp.D[4],
        }
    )

    symbol = BoxSymbol()


class QuadColumnComponent(Component):
    lp = QuadColumnLandpattern(num_rows=(4, 3)).lead_profile(
        pitch=1.27, span=7 * 1.27, length=1.27, width=0.4, protrusion=SmallGullWingLeads
    )

    A = Port(), Port(), Port(), Port()
    B = Port(), Port(), Port()
    C = Port(), Port(), Port(), Port()
    D = Port(), Port(), Port()

    symbol = BoxSymbol()


class BGAComponent(Component):
    @inline
    class lp(BGA):
        def __init__(self):
            super().__init__(
                num_rows=4,
                num_cols=4,
                ball_diameter=1.0,
                pitch=1.27,
            )

        def __base_init__(self):
            super().__base_init__()
            self.pad_config(SMDPadConfig()).grid_planner(
                lambda pos, h, w: pos.row != pos.column
            ).silkscreen_outline(
                SoldermaskBased().silkscreen_line(
                    SilkscreenLine.Vertical
                    | SilkscreenLine.XAxis
                    | SilkscreenLine.YAxis
                )
            )

    A = Port(), Port(), Port()
    B = Port(), Port(), Port()
    C = Port(), Port(), Port()
    D = Port(), Port(), Port()

    symbol = BoxSymbol()


class MySOIC(Component):
    landpattern = SOIC(num_leads=14).narrow(10)

    ports = [Port() for _ in range(14)]
    symbol = BoxSymbol()


class MyWideSOIC(Component):
    landpattern = SOIC(num_leads=14).wide(10).silkscreen_outline(PackageBased())

    ports = [Port() for _ in range(14)]
    symbol = BoxSymbol()


class MyQFN(Component):
    landpattern = (
        QFN(num_rows=(8, 7))
        .density_level("A")
        .lead_profile(
            LeadProfile(
                span=Toleranced(4.2, 0.05),
                pitch=0.5,
                type=QFNLead(
                    length=Toleranced(0.4, 0.05),
                    width=Toleranced(0.25, 0.05),
                ),
            ),
            LeadProfile(
                span=Toleranced(4.8, 0.05),
                pitch=0.5,
                type=QFNLead(
                    length=Toleranced(0.4, 0.05),
                    width=Toleranced(0.25, 0.05),
                ),
            ),
        )
        .thermal_pad(
            shape=rectangle(2.8, 3.4),
            config=SMDPadConfig(paste=WindowSubdivide(gridShape=(3, 3))),
        )
        .corner_pad_chamfer(0.1)
        .silkscreen_outline(
            SoldermaskBased().silkscreen_line(SilkscreenLine.Perimeter, -0.05)
        )
    )

    ports = [Port() for _ in range(16)]
    symbol = BoxSymbol()


class LandpatternGeneratorTestDesign(SampleDesign):
    @inline
    class circuit(Circuit):
        dual = DualColumnComponent()
        quad = QuadColumnComponent()
        weird = WeirdQuadColumnComponent()
        bga = BGAComponent()
        soic = MySOIC()
        wide_soic = MyWideSOIC()
        qfn = MyQFN()

        def __init__(self):
            # Rebuilding the landpattern after the fact breaks the padmapping,
            # unless a default mapping is used (which is resolved at translation).
            # TODO: should pads be "remapped" to their new pads to allow this?
            # self.dual.lp.silkscreen_outline(
            #     SoldermaskBased().silkscreen_line(
            #         SilkscreenLine.Vertical
            #     )
            # ).rebuild(force=True)
            pass


class SimpleQuadTestDesign(SampleDesign):
    @inline
    class circuit(Circuit):
        @inline
        class quad(Component):
            symbol = BoxSymbol()
            lp = (
                QFN(num_leads=8)
                .lead_profile(
                    LeadProfile(
                        span=Toleranced(1.7, 0.05),
                        pitch=0.5,
                        type=QFNLead(
                            length=Toleranced(0.4, 0.05),
                            width=Toleranced(0.25, 0.05),
                        ),
                    )
                )
                .corner_pad_chamfer(0.15)
                .silkscreen_outline(
                    SoldermaskBased()
                    .silkscreen_line(SilkscreenLine.Perimeter, -0.2)
                    .line_width(0.30)
                )
            )


class LandpatternGeneratorTestCase(jitx.test.TestCase):
    def test_initialize_directly(self):
        with SubstrateContext(SampleSubstrate()):
            lp = DualColumnLandpattern(num_rows=3).lead_profile(
                pitch=1.27,
                span=1.27,
                length=1.27,
                width=0.4,
                protrusion=SmallGullWingLeads,
            )
            # lp.rebuild()
        self.assertSetEqual(set(lp.A), {1, 2, 3})
        self.assertSetEqual(set(lp.B), {1, 2, 3})

    def test_initialize_via_component(self):
        with SubstrateContext(SampleSubstrate()):
            c = DualColumnComponent()
        self.assertSetEqual(set(c.lp.A), {1, 2, 3})
        self.assertSetEqual(set(c.lp.B), {1, 2, 3})

    def test_initialize_linear(self):
        with SubstrateContext(SampleSubstrate()):
            lp = DualColumnLinearLandpattern(num_rows=3)
        self.assertSetEqual(set(lp.p), {1, 2, 3, 4, 5, 6})

    def test_initialize_quad(self):
        with SubstrateContext(SampleSubstrate()):
            lp = QuadColumnLandpattern(num_rows=(2, 2, 3, 3)).lead_profile(
                pitch=1.27,
                span=3 * 1.27,
                length=1.27,
                width=0.4,
                protrusion=SmallGullWingLeads,
            )
        self.assertSetEqual(set(lp.A), {1, 2})
        self.assertSetEqual(set(lp.B), {1, 2})
        self.assertSetEqual(set(lp.C), {1, 2, 3})
        self.assertSetEqual(set(lp.D), {1, 2, 3})

    def test_initialize_quad_via_component(self):
        with SubstrateContext(SampleSubstrate()):
            c = QuadColumnComponent()
        self.assertSetEqual(set(c.lp.A), {1, 2, 3, 4})
        self.assertSetEqual(set(c.lp.B), {1, 2, 3})
        self.assertSetEqual(set(c.lp.C), {1, 2, 3, 4})
        self.assertSetEqual(set(c.lp.D), {1, 2, 3})
