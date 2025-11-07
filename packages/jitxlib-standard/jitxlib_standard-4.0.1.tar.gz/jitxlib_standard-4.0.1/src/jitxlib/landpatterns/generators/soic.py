import dataclasses

from jitx.anchor import Anchor
from jitx.toleranced import Toleranced

from ..courtyard import ExcessCourtyard
from ..dual import DualColumn
from ..grid_layout import LinearNumbering
from ..leads import LeadProfile, SMDLead
from ..leads.protrusions import BigGullWingLeads
from ..package import PackageBodyMixin, RectanglePackage
from ..pads import SMDPadConfig, ThermalPadGeneratorMixin
from ..silkscreen.labels import ReferenceDesignatorMixin
from ..silkscreen.marker import Pad1Marker
from ..silkscreen.outlines import SilkscreenOutline


SOIC_DEFAULT_LEAD_PROFILE = LeadProfile(
    pitch=1.27,
    span=Toleranced.min_max(3.8, 4.0),
    type=SMDLead(
        length=Toleranced.min_max(0.4, 1.27),
        width=Toleranced.min_max(0.31, 0.51),
        lead_type=BigGullWingLeads,
    ),
)


class SOICBase(ThermalPadGeneratorMixin, PackageBodyMixin, DualColumn):
    """Small Outline Integrated Circuit (SOIC) Landpattern

    This class generates a full SOIC landpattern. By default, it creates a
    soldermask-bounds-based silkscreen outline, a circular pad 1 marker, and
    a courtyard based on the bounds of all features buffered by an excess
    amount. It can also optionally generate a thermal pad.
    """

    def __base_init__(self):
        super().__base_init__()
        self.lead_profile(SOIC_DEFAULT_LEAD_PROFILE)
        self.pad_config(SMDPadConfig())

    def narrow(
        self,
        package_length: Toleranced | float,
        *,
        span: Toleranced | float | None = None,
    ):
        """Set the package body to be standard narrow SOIC

        >>> class MySOIC(Component):
        ...     # A narrow body SOIC, 10 mm long, with 14 leads
        ...     landpattern = SOIC(num_leads=14).narrow(10)

        Args:
            package_length: length of the package body
            span: span of the leads. If not specified, the span is set to the width of the package body

        Returns:
            self for method chaining
        """
        lp = self._lead_profiles()[0]
        width = Toleranced.min_max(3.8, 4.0)
        self.package_body(
            RectanglePackage(
                length=Toleranced.exact(package_length),
                width=width,
                height=Toleranced.min_max(1.35, 1.75),
            )
        )
        self.lead_profile(dataclasses.replace(lp, span=Toleranced.exact(span or width)))
        return self

    def wide(
        self,
        package_length: Toleranced | float,
        *,
        span: Toleranced | float | None = None,
    ):
        """Set the package body to be standard narrow SOIC.

        Args:
            package_length: length of the package body
            span: span of the leads. If not specified, the span is set to the width of the package body

        Returns:
            self for method chaining
        """
        lp = self._lead_profiles()[0]
        width = Toleranced.min_max(7.4, 7.6)
        self.package_body(
            RectanglePackage(
                length=Toleranced.exact(package_length),
                width=width,
                height=Toleranced.min_max(2.35, 2.65),
            )
        )
        self.lead_profile(dataclasses.replace(lp, span=Toleranced.exact(span or width)))
        return self


class SOICDecorated(
    SilkscreenOutline, Pad1Marker, ReferenceDesignatorMixin, ExcessCourtyard, SOICBase
):
    def __base_init__(self):
        super().__base_init__()
        self.pad_1_marker_direction(Anchor.W)


class SOIC(LinearNumbering, SOICDecorated):
    """Small Outline Integrated Circuit (SOIC) Landpattern

    This class generates a full SOIC landpattern. By default, it creates a
    soldermask-bounds-based silkscreen outline, a circular pad 1 marker, and
    a courtyard based on the bounds of all features buffered by an excess
    amount. It can also optionally generate a thermal pad.

    Note that this class will use :py:class:`~LinearNumbering` for the pad
    numbering. To use a different numbering scheme, create a subclass of
    :py:class:`~SOICDecorated` and inherit a different one.

    >>> class MySOIC(Component):
    ...     # A narrow body SOIC, 10 mm long, with 14 leads
    ...     landpattern = SOIC(num_leads=14).narrow(10)
    >>> MySOIC().landpattern.p[1]
    SMDPad
    """
