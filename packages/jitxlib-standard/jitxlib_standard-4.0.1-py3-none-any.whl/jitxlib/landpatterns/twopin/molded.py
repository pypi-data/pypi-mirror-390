from collections.abc import Iterable
from typing import override

from jitx.shapes.composites import rectangle
from jitx.toleranced import Toleranced
from jitx.transform import Transform

from .. import LandpatternGenerator
from ..courtyard import ExcessCourtyard, OriginMarkerMixin
from ..grid_layout import GridPosition, LinearNumbering
from ..ipc import DensityLevelMixin, IPCRequirements, compute_ipc
from ..keepout import KeepoutGeneratorMixin
from ..leads import LeadProfile, SMDLead
from ..leads.protrusions import BigRectangularLeads
from ..pads import GridPadShapeGeneratorMixin, SMDPadConfig
from ..silkscreen.marker import Pad1Marker
from ..silkscreen.outlines import SilkscreenLine, SilkscreenOutline, SoldermaskBased
from ..twopin.smt import CathodeAnodeNumbering


MOLDED_DEFAULT_PROTRUSION = BigRectangularLeads


class MoldedTwoPinBase(
    DensityLevelMixin, GridPadShapeGeneratorMixin, LandpatternGenerator
):
    _num_rows = 2
    _num_cols = 1

    # cached value, cleared on build
    __computed_ipc: IPCRequirements | None = None

    def __init__(self, lead_span: Toleranced, lead: SMDLead):
        super().__init__()
        self.__lead_span = lead_span
        self.__lead = lead

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
    def _pad_shape(self, pos: GridPosition):
        pad_y, pad_x = self.__compute_ipc().pad_size()
        return rectangle(pad_x, pad_y)

    @override
    def _generate_layout(self) -> Iterable[GridPosition]:
        half_spacing = self._lead_spacing / 2.0
        return (
            GridPosition(0, 0, Transform.translate(0.0, half_spacing)),
            GridPosition(1, 0, Transform.translate(0.0, -half_spacing)),
        )

    def __compute_ipc(self):
        if self.__computed_ipc is not None:
            return self.__computed_ipc
        density_level = self._density_level
        lead_profile = LeadProfile(self.__lead_span, 0.0, self.__lead)
        lead_span = lead_profile.span
        lead_width = lead_profile.type.width
        lead_protrusion = lead_profile.type.lead_type
        lead_fillets = lead_protrusion.fillets[density_level]
        self.__computed_ipc = compute_ipc(
            lead_span,
            lead_profile.type.length,
            lead_width,
            lead_fillets,
        )
        return self.__computed_ipc


class MoldedTwoPinDecorated(
    KeepoutGeneratorMixin,
    SilkscreenOutline,
    OriginMarkerMixin,
    ExcessCourtyard,
    MoldedTwoPinBase,
):
    def __base_init__(self):
        super().__base_init__()
        self.silkscreen_outline(
            SoldermaskBased().silkscreen_line(SilkscreenLine.Vertical)
        )


class PolarizedMoldedTwoPin(CathodeAnodeNumbering, Pad1Marker, MoldedTwoPinDecorated):
    pass


class MoldedTwoPin(LinearNumbering, MoldedTwoPinDecorated):
    pass
