"""
Small Outline Transistor (SOT) Landpattern Generator
====================================================

This module provides a base class for generating SOT landpatterns, and a set of
concrete subclasses for specific SOT packages. A
:py:class:`~jitxlib.landpatterns.leads.LeadProfile` must be provided
for the landpattern to be complete or an error will be raised, but everything
else is optional. The :py:class:`SOTLeadProfile` class is provided as a
shorthand for common lead profile values.

A trivial example of a three-port SOT component is shown below:

>>> from jitx import Component, Port, Toleranced as T
>>> from jitxlib.landpatterns.generators.sot import SOT23_3, SOTLeadProfile
>>> from jitxlib.landpatterns.package import RectanglePackage
>>> from jitxlib.symbols.box import BoxSymbol
>>> class MyComponent(Component):
...     "Trivial three-port SOT component."
...     VCC = Port()
...     OUT = Port()
...     GND = Port()
...
...     landpattern = SOT23_3().package_body(
...         RectanglePackage(
...             width=T.min_max(1.2, 1.4),
...             length=T.min_max(2.8, 3.0),
...             height=T.min_max(0.9, 1.15),
...         )
...     ).lead_profile(
...         SOTLeadProfile(
...             span=T.min_max(2.25, 2.55),
...         )
...     )
...
...     symbol = BoxSymbol()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import override

from jitx.anchor import Anchor
from jitx.toleranced import Toleranced as T

from ..courtyard import ExcessCourtyard
from ..dual import DualColumn
from ..grid_layout import GridPosition, LinearNumbering
from ..leads import LeadProfile, SMDLead
from ..leads.protrusions import (
    LeadProtrusion,
    SmallGullWingLeads,
    SmallOutlineFlatLeads,
)
from ..package import PackageBodyMixin
from ..pads import SMDPadConfig, ThermalPadGeneratorMixin
from ..silkscreen.labels import ReferenceDesignatorMixin
from ..silkscreen.marker import Pad1Marker
from ..silkscreen.outlines import SilkscreenOutline


@dataclass(frozen=True)
class SOTLead(SMDLead):
    """SOT Lead

    This class specifies the default lead for SOT landpatterns. Please examine
    the values to make sure they are correct for your application, and override
    them with the values from the datasheet as necessary.
    """

    length: T = T.min_max(0.3, 0.55)
    """Length of the SMT lead in mm, default 0.3 to 0.55 mm"""

    width: T = T.min_max(0.3, 0.5)
    """Width of the SMT lead in mm, default 0.3 to 0.5 mm"""

    lead_type: LeadProtrusion = SmallGullWingLeads
    """Lead Protrusion Type

    The default value for SOT leads is :py:class:`~SmallGullWingLeads`.
    """


@dataclass(frozen=True)
class SOTFlatLead(SOTLead):
    """SOT Flat Lead

    This class specifies the default lead for flat SOT landpatterns.
    """

    lead_type: LeadProtrusion = SmallOutlineFlatLeads
    """Lead Protrusion Type

    The default value for SOT flat leads is :py:class:`~SmallOutlineFlatLeads`.
    Used for packages like SOT-23F or SOT538.
    """


@dataclass(frozen=True)
class SOTLeadProfile(LeadProfile):
    """SOT Lead Profile

    This is a convenience subclass that specifies a default set of lead profile
    values for SOT landpatterns, in particular it sets the pitch to 0.95 mm and
    uses the :py:class:`SOTLead` lead type, but still requiring ``span`` to be
    defined by the user. Both pitch and lead type can naturally also be
    overridden, or a fully specified :py:class:`LeadProfile` can be used
    instead.
    """

    pitch: float = 0.95
    """Pitch - the distance between adjacent leads on the same side of the
    package, default 0.95 mm
    """

    type: SOTLead = SOTLead()
    """The lead type for this profile, default :py:class:`~SOTLead`"""


SOT_DEFAULT_PITCH = SOTLeadProfile.pitch
SOT_DEFAULT_PROTRUSION = SOTLead.lead_type


class SOTBase(ThermalPadGeneratorMixin, PackageBodyMixin, DualColumn):
    """Small Outline Transistor (SOT) Landpattern Generator Base"""

    def __base_init__(self):
        super().__base_init__()
        self.pad_config(SMDPadConfig())

    _SOT_grid: tuple[
        tuple[bool, bool],
        tuple[bool, bool],
        tuple[bool, bool],
    ] = ((False, False), (False, False), (False, False))

    def __init__(self):
        super().__init__(num_rows=3)

    @override
    def _active_pad(self, pos: GridPosition) -> bool:
        return self._SOT_grid[pos.row][pos.column]


class SOTDecorated(
    SilkscreenOutline, Pad1Marker, ReferenceDesignatorMixin, ExcessCourtyard, SOTBase
):
    """Decorated SOT Landpattern Generator, with no pad numbering scheme"""

    def __base_init__(self):
        super().__base_init__()
        self.pad_1_marker_direction(Anchor.W)


class SOT(LinearNumbering, SOTDecorated):
    """SOT Landpattern Generator, with a linear numbering scheme. It's a base
    class for SOT devices, and should not be used directly, instead use one of
    the subclasses that define actual pad layouts, e.g. :py:class:`SOT23_3`."""


class SOT23(SOT):
    """SOT-23 base class. This is currenetly only used as a marker base class.
    Please use one of the subclasses that define actual pad layouts, e.g.
    :py:class:`SOT23_3`."""


class SOT23_3(SOT23):
    """SOT-23-3 Landpattern Generator

    Pads are generated in the following layout:

    .. code-block:: text

        1
          3
        2
    """

    _SOT_grid = (
        (True, False),
        (False, True),
        (True, False),
    )


class SOT23_5(SOT23):
    """SOT-23-5 Landpattern Generator

    Pads are generated in the following layout:

    .. code-block:: text

        1 5
        2
        3 4
    """

    _SOT_grid = (
        (True, True),
        (True, False),
        (True, True),
    )


class SOT23_6(SOT23):
    """SOT-23-6 Landpattern Generator

    Pads are generated in the following layout:

    .. code-block:: text

        1 6
        2 5
        3 4
    """

    _SOT_grid = (
        (True, True),
        (True, True),
        (True, True),
    )
