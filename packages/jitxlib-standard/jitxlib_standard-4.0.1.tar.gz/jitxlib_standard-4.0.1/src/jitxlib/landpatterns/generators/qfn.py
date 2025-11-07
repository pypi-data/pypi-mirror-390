"""
The QFN Landpattern Generator
=============================

The QFN landpattern has three basic entry points for generating a QFN
landpattern, the :py:class:`~QFN`, :py:class:`QFNDecorated`, and
:py:class:`~QFNBase` classes. The :py:class:`~QFN` is the most off-the-shelf
class which has the most defaults set, including a numbering scheme using
:py:class:`~jitxlib.landpatterns.grid_layout.LinearNumbering`, with pads
starting at ``.p[1]`` in the top-left, going counter-clockwise around the chip.
The :py:class:`~QFNDecorated` class is the same landpattern, including
silkscreen decorations but without a numbering scheme.  It's not usable as-is,
and needs to be subclassed, mixing in a numbering scheme. Finally there's the
:py:class:`~QFNBase` class, which is the most basic class, which only declares
the pads, with no silkscreen decorations.

A QFN is based on the :py:class:`~jitxlib.landpatterns.quad.QuadColumn` class,
which generates 4 "columns" of leads, and can be instantiated with either the
number of leads (divisible by 4, distributed evenly on all sides) or the number
of rows, which are laid out on each side. Optionally the number of rows can be
a two-tuple to specify a different number of rows on left/right and top/bottom.

>>> class MyComponent(Component):
...     landpattern = QFN(num_leads=16)  # 4 leads on each side, 16 total

>>> class MyComponent(Component):
...     landpattern = QFN(num_rows=4)  # 4 leads on each side, 16 total

>>> class MyComponent(Component):
...     landpattern = QFN(num_rows=(4, 6))  # 4 on left/right, 6 on top/bottom

To further customize the landpattern, various customization methods are
available, the main one being the
:py:meth:`~jitxlib.landpatterns.leads.LeadProfileMixin.lead_profile`,
which allows specifying the lead profile for the landpattern using a
:py:class:`~jitxlib.landpatterns.leads.LeadProfile` object. If no other
mechanism is used to declare size and placement, this call is required.

A full example of a QFN component could look something like this:

>>> from jitx.toleranced import Toleranced as T
>>> from jitxlib.landpatterns.generators.qfn import QFN, QFNLead
>>> from jitxlib.landpatterns.ipc import DensityLevel
>>> from jitxlib.landpatterns.leads import LeadProfile
>>> from jitxlib.landpatterns.package import RectanglePackage
>>> from jitxlib.landpatterns.pads import SMDPadConfig, WindowSubdivide
>>> from jitxlib.symbols.box import BoxSymbol
>>> class QFNComponent(Component):
...     A = Port(), Port(), Port(), Port()
...     B = Port(), Port(), Port(), Port()
...     C = Port(), Port(), Port(), Port()
...     D = Port(), Port(), Port(), Port()
...     GND = Port()
...     def __init__(self):
...         self.symbol = BoxSymbol()
...         width = T(5.0, 0.05)
...         height = T(0.8, 0.05)
...         pitch = 0.5
...         lead_length = T(0.4, 0.05)
...         lead_width = T(0.25, 0.05)
...         package_body = RectanglePackage(width=width, length=width, height=height)
...         self.landpattern = (
...             QFN(num_leads=16)
...             .package_body(package_body)
...             .density_level(DensityLevel.A)
...             .thermal_pad(
...                 shape=rectangle(3.7, 3.7),
...                 config=SMDPadConfig(paste=WindowSubdivide(padding=0.25)),
...             )
...             .lead_profile(LeadProfile(width, pitch, QFNLead(lead_length, lead_width)))
...         )

Note that we're using the default pad-mapping here which will map the declared
ports in order, ending with the thermal pad. If you want your ports organized
differently you need to also declare a :py:class:`~jitx.landpattern.PadMapping`
where the pins are accessible through ``self.landpattern.p[1]``` up to and
including ``.p[16]`` with the additional thermal pad accessible as
``.thermal_pads[0]``.

It's also worth noting that the density level is optional, and if not specified
it will be read from the context which can be set for the entire design (or
circuit) using the :py:class:`~jitxlib.landpatterns.ipc.DensityLevelContext`,
which defaults to ``C`` if unset.
"""

from dataclasses import dataclass

from jitx.anchor import Anchor
from ..courtyard import ExcessCourtyard
from ..grid_layout import A1, LinearNumbering
from ..leads import SMDLead
from ..leads.protrusion import LeadProtrusion
from ..leads.protrusions import QuadFlatNoLeads
from ..pads import SMDPadConfig, ThermalPadGeneratorMixin
from ..quad import CornerPadChamfer, QuadColumn
from ..silkscreen.labels import ReferenceDesignatorMixin
from ..silkscreen.marker import Pad1Marker
from ..silkscreen.outlines import SilkscreenOutline


@dataclass(frozen=True)
class QFNLead(SMDLead):
    """QFN Lead

    This class specifies the default lead for QFN landpatterns.
    """

    lead_type: LeadProtrusion = QuadFlatNoLeads
    """Lead Protrusion Type

    The default value for QFN leads is :py:class:`~QuadFlatNoLeads`.
    """


class QFNBase(CornerPadChamfer, ThermalPadGeneratorMixin, QuadColumn):
    """QFN Landpattern Generator Base"""

    def __base_init__(self):
        super().__base_init__()
        self.pad_config(SMDPadConfig())


class QFNDecorated(
    SilkscreenOutline, Pad1Marker, ReferenceDesignatorMixin, ExcessCourtyard, QFNBase
):
    """Decorated QFN Landpattern Generator, with no pad numbering scheme."""

    def __base_init__(self):
        super().__base_init__()
        self.pad_1_marker_direction(Anchor.W)


class QFN(A1, LinearNumbering, QFNDecorated):
    """QFN Landpattern Generator"""
