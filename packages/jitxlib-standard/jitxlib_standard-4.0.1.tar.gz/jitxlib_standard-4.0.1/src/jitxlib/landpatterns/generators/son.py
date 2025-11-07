from dataclasses import dataclass

from jitx.anchor import Anchor

from ..courtyard import ExcessCourtyard
from ..dual import DualColumn
from ..grid_layout import LinearNumbering
from ..leads import SMDLead
from ..leads.protrusions import LeadProtrusion, SmallOutlineNoLeads
from ..package import PackageBodyMixin
from ..pads import SMDPadConfig, ThermalPadGeneratorMixin
from ..silkscreen.labels import ReferenceDesignatorMixin
from ..silkscreen.marker import Pad1Marker
from ..silkscreen.outlines import SilkscreenOutline


SON_DEFAULT_PROTRUSION = SmallOutlineNoLeads


@dataclass(frozen=True)
class SONLead(SMDLead):
    """SON Lead

    This class specifies the default lead for SON landpatterns.
    """

    lead_type: LeadProtrusion = SON_DEFAULT_PROTRUSION
    """Lead Protrusion Type

    The default value for SOP leads is :py:class:`~SmallGullWingLeads`.
    """


class SONBase(ThermalPadGeneratorMixin, PackageBodyMixin, DualColumn):
    """Small Outline No-Lead (SON) Landpattern

    This class generates a full SON landpattern. By default, it creates a
    soldermask-bounds-based silkscreen outline, a circular pad 1 marker, and
    a courtyard based on the bounds of all features buffered by an excess
    amount. It can also optionally generate a thermal pad.
    """

    def __base_init__(self):
        super().__base_init__()
        self.pad_config(SMDPadConfig())


class SONDecorated(
    SilkscreenOutline, Pad1Marker, ReferenceDesignatorMixin, ExcessCourtyard, SONBase
):
    """Decorated SON Landpattern Generator, with no pad numbering scheme."""

    def __base_init__(self):
        super().__base_init__()
        self.pad_1_marker_direction(Anchor.W)


class SON(LinearNumbering, SONDecorated):
    """Small Outline No-Lead (SON) Landpattern

    This class generates a full SON landpattern. By default, it creates a
    soldermask-bounds-based silkscreen outline, a circular pad 1 marker, and
    a courtyard based on the bounds of all features buffered by an excess
    amount. It can also optionally generate a thermal pad.

    Note that this class will use :py:class:`~LinearNumbering` for the pad
    numbering. To use a different numbering scheme, create a subclass of
    :py:class:`~SONBase` and inherit a different one.

    >>> class MySON(Component):
    ...     # A 14-lead SON
    ...     landpattern = (
    ...         SON(
    ...             num_leads=14,
    ...         )
    ...         .lead_profile(
    ...             LeadProfile(
    ...                 span=Toleranced.min_max(6.2, 6.6),
    ...                 pitch=0.65,
    ...                 type=SONLead(
    ...                     length=Toleranced.min_max(0.5, 0.75),
    ...                     width=Toleranced.min_max(0.19, 0.3),
    ...                 ),
    ...             ),
    ...         )
    ...         .package_body(
    ...             RectanglePackage(
    ...                 width=Toleranced.min_max(4.3, 4.5),
    ...                 length=Toleranced(5.0, 0.1),
    ...                 height=Toleranced.min_max(1.0, 1.2),
    ...             )
    ...         )
    ...     )
    >>> MySON().landpattern.p[1]
    SMDPad
    """
