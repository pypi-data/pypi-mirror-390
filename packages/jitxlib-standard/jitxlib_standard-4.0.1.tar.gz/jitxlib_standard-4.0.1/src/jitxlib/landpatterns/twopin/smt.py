from collections.abc import Iterable
from typing import override
from jitx._structural import Structurable
from jitx.landpattern import Pad
from jitx.shapes import Shape
from jitx.shapes.composites import rectangle
from jitx.toleranced import Toleranced
from jitx.transform import Transform
from .. import LandpatternGenerator
from ..courtyard import ExcessCourtyard, OriginMarkerMixin
from ..grid_layout import GridLayoutInterface, GridPosition, LinearNumbering
from ..ipc import DensityLevelMixin, IPCRequirements, compute_ipc
from ..leads import LeadProfile, LeadProfileMixin, SMDLead
from ..leads.protrusions import BigRectangularLeads, SmallRectangularLeads
from ..package import PackageBodyMixin, RectanglePackage
from ..pads import GridPadShapeGeneratorMixin, SMDPadConfig
from ..silkscreen.marker import Pad1Marker
from ..silkscreen.outlines import (
    InterstitialOutline,
    SilkscreenLine,
    SilkscreenOutline,
    SoldermaskBased,
)
from .SMT_table import SMT_CHIP_DEFS


SMT_DEFAULT_HEIGHT = Toleranced(0.4, 0.1)


class SMTBase(
    PackageBodyMixin,
    LeadProfileMixin,
    DensityLevelMixin,
    GridPadShapeGeneratorMixin,
    GridLayoutInterface,
    LandpatternGenerator,
):
    _num_rows: int = 2
    _num_cols: int = 1

    __side_fillet: float = 0

    # cached value, cleared on build
    __computed_ipc: IPCRequirements | None = None

    def __init__(
        self,
        case_name: str,
        *,
        side_fillet: float | None = None,
        height: Toleranced | None = None,
    ):
        super().__init__()
        self._case_name = case_name
        chip = SMT_CHIP_DEFS[case_name]
        # not used outside the constructor at the moment
        # self.__chip_def = chip
        self.lead_profile(
            LeadProfile(
                pitch=3.14159,  # not used
                span=chip.length,
                type=SMDLead(
                    length=chip.lead_length,
                    width=chip.lead_width,
                    lead_type=BigRectangularLeads
                    if chip.width.typ > 0.8
                    else SmallRectangularLeads,
                ),
            )
        )
        if side_fillet is not None:
            self.__side_fillet = side_fillet
        self.package_body(
            RectanglePackage(
                width=chip.width,
                length=chip.length,
                height=height or SMT_DEFAULT_HEIGHT,
            )
        )

    def __base_init__(self):
        super().__base_init__()
        self.pad_config(SMDPadConfig())

    @override
    def _build(self):
        self.__computed_ipc = None
        super()._build()

    @property
    def _lead_spacing(self) -> float:
        ipc = self.__compute_ipc()
        return ipc.Gmin + ipc.pad_size()[0]

    @override
    def _pad_shape(self, pos: GridPosition) -> Shape:
        pad_y, pad_x = self.__compute_ipc().pad_size()
        return rectangle(pad_x, pad_y)

    def _generate_layout(self) -> Iterable[GridPosition]:
        half = self._lead_spacing / 2.0
        return (
            GridPosition(0, 0, Transform.translate(0.0, half)),
            GridPosition(1, 0, Transform.translate(0.0, -half)),
        )

    def __compute_ipc(self):
        if self.__computed_ipc is not None:
            return self.__computed_ipc
        density_level = self._density_level
        lprofile = self._lead_profiles()[0]
        lead_span = lprofile.span
        lead_width = lprofile.type.width + 2.0 * self.__side_fillet
        lead_protrusion = lprofile.type.lead_type
        lead_fillets = lead_protrusion.fillets[density_level]
        self.__computed_ipc = compute_ipc(
            lead_span,
            lprofile.type.length,
            lead_width,
            lead_fillets,
        )
        return self.__computed_ipc


class SMTDecorated(SilkscreenOutline, OriginMarkerMixin, ExcessCourtyard, SMTBase):
    def __base_init__(self):
        super().__base_init__()
        self.silkscreen_outline(
            InterstitialOutline(horizontal=True).silkscreen_line(
                SilkscreenLine.Vertical
            ),
            SoldermaskBased().silkscreen_line(SilkscreenLine.XAxis),
        )


class CathodeAnodeNumbering(GridLayoutInterface):
    a: Pad | None = None
    c: Pad | None = None

    @override
    def _build(self):
        for p in (self.a, self.c):
            if p is not None:
                Structurable._dispose(p)
        self.a = None
        self.c = None
        super()._build()

    @override
    def _assign_pad(self, r: int, c: int, pad: Pad):
        if r not in (0, 1) or c != 0:
            raise ValueError("CathodeAnodeNumbering only supports 2 rows and 1 column")
        if r == 0:  # anode
            self.a = pad
        else:  # cathode
            self.c = pad


class PolarizedSMT(CathodeAnodeNumbering, Pad1Marker, SMTDecorated):
    pass


class SMT(LinearNumbering, SMTDecorated):
    pass


class O4O2(SMT):
    def __init__(self):
        super().__init__(case_name="0402")
