from dataclasses import dataclass

from jitx.anchor import Anchor

from ..courtyard import ExcessCourtyard
from ..grid_layout import A1, LinearNumbering
from ..leads import SMDLead
from ..leads.protrusion import LeadProtrusion
from ..leads.protrusions import BigGullWingLeads
from ..pads import SMDPadConfig, ThermalPadGeneratorMixin
from ..quad import CornerPadChamfer, QuadColumn
from ..silkscreen.labels import ReferenceDesignatorMixin
from ..silkscreen.marker import Pad1Marker
from ..silkscreen.outlines import SilkscreenOutline


@dataclass(frozen=True)
class QFPLead(SMDLead):
    """QFP Lead

    This class specifies the default lead for QFP landpatterns.
    """

    lead_type: LeadProtrusion = BigGullWingLeads
    """Lead Protrusion Type

    The default value for QFP leads is :py:class:`~BigGullWingLeads`.
    """


class QFPBase(CornerPadChamfer, ThermalPadGeneratorMixin, QuadColumn):
    """QFP Landpattern Generator Base"""

    def __base_init__(self):
        super().__base_init__()
        self.pad_config(SMDPadConfig())


class QFPDecorated(
    SilkscreenOutline, Pad1Marker, ReferenceDesignatorMixin, ExcessCourtyard, QFPBase
):
    """Decorated QFP Landpattern Generator, with no pad numbering scheme."""

    def __base_init__(self):
        super().__base_init__()
        self.pad_1_marker_direction(Anchor.W)


class QFP(A1, LinearNumbering, QFPDecorated):
    """QFP Landpattern Generator"""
