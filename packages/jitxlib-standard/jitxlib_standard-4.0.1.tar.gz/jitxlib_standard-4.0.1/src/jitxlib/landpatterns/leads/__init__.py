from dataclasses import dataclass
from collections.abc import Sequence
from typing import Self, overload

from jitx.toleranced import Toleranced

from ..ipc import DensityLevelMixin, DensityLevel, IPCRequirements, compute_ipc
from .protrusion import LeadProtrusion


@dataclass(frozen=True)
class SMDLead:
    """Surface Mount Lead Descriptor"""

    length: Toleranced
    """Length of the SMT lead in mm

    This is typically the "foot length" of a lead. In JEDEC
    drawings this dimension is typically identified as 'L'.
    """
    width: Toleranced
    """Width of the SMT lead in mm

    In JEDEC drawings this dimension is typically identified as 'b'.
    """

    lead_type: LeadProtrusion
    """ Lead Protrusion Type

    This type captures typical features for this kind of lead.
    """

    # TODO
    # override: Pad | None = None
    # """ Optional Override Pad for this Lead Type
    # """

    def __post_init__(self):
        # TODO - check toleranced > 0
        pass

    def compute_constraints(
        self, lead_span: Toleranced, density_level: DensityLevel
    ) -> IPCRequirements:
        """Compute the IPC-7351B-based pad constraints for this lead type

        Args:
            lead_span: the lead span for the package
            density_level: the density level for the package

        Returns:
            the IPC computation results for this lead type and density level
        """
        # TODO handle `override` here
        return compute_ipc(
            lead_span, self.length, self.width, self.lead_type.fillets[density_level]
        )

    def pad_size(self, density_level: DensityLevel) -> tuple[float, float]:
        """Compute the pad size for this lead type

        Args:
            density_level: the density level for the package

        Returns:
            the pad size (width, height) for this lead type and density level
        """
        fillet = self.lead_type.fillets[density_level]
        length = self.length.typ + fillet.toe + fillet.heel
        width = self.width.max_value + 2.0 * fillet.side
        return (length, width)


@dataclass(frozen=True)
class THLead:
    """Through Hole Lead Descriptor
    This type of lead is typically used for axial through-hole resistors,
    radial through-hole capacitors, or DIP style ICs.
    """

    length: Toleranced
    """Length of the through-hole lead in mm

    The length of the lead is measured from the body of the
    component to the end of the lead.

    For components where the lead lengths are different (for example,
    with electrolytic capacitors), this length describes the minimum
    common length.
    """

    width: Toleranced
    """Width of the through-hole lead
    Usually the diameter of the lead, for rectangular leads this is the
    diagonal measurement of the lead.
    """

    # TODO
    # override: Pad | None = None
    # """Override the generated through-hole pad with this explicit pad.
    # """

    def __post_init__(self):
        # TODO - check toleranced > 0
        pass


@dataclass
class LeadPlacement:
    """This class encapsultes the data necessary to place
    the pads associated with a `LeadProfile`
    """

    pad_size: tuple[float, float]
    """Pad Size as a (width, height) tuple where
    - `width` is aligned to the X-axis in mm
    - `height` is aligned to the Y-axis in mm
    """

    center: float
    """Center to center distance in the lead-span direction.
    Value in mm.
    """

    pitch: float
    """Center to Center distance between adjacent pads on one edge side.
    Value in mm.
    """


@dataclass(frozen=True)
class LeadProfile:
    """Lead Profile Package Pad Descriptor

    This class describes the dimensions for a set of opposing pads on a package.
    For many IC packages, like dual packages (SOICs, SSOPs, etc) or quad
    packages (QFNs, QFPs, etc), there are one or more "lead profiles".

    In a dual package, there is typically one lead profile across the width
    of the dual row package. The lead profile describes:

    1. Lead Span - this distance from the edge of the leads on one side to the
       edge of the leads on the other side of the component
    2. Pitch - Distance between adjacent leads on the same side of the package.
    3. Lead Type - the type of lead protrusions found on either side of the component.

    TODO - Diagram Here

    In a quad package, there are potentially two different lead profiles, one for
    left/right edges of the package and one for the top/bottom edges of the package.

    .. seealso::

        IPC-7351B Figure 3-3
    """

    span: Toleranced
    """Lead Span - the distance from the edge of the leads on one side to the
    edge of the leads on the other side of the component, from outside edge of
    the lead to outside edge of the opposite lead.
    """

    pitch: float
    """Pitch - the distance between adjacent leads on the same side of the
    package
    """

    type: SMDLead
    """The lead type for this profile"""

    def compute_placements(self, density_level: DensityLevel) -> LeadPlacement:
        """Compute the lead placements for this lead profile

        Args:
            density_level: the density level for the package

        Returns:
            the lead placements for this lead profile
        """

        ipcData = self.type.compute_constraints(self.span, density_level)
        padSize = ipcData.pad_size()
        delta = ipcData.Gmin + padSize[0]  # X
        return LeadPlacement(padSize, delta, self.pitch)


class LeadProfileMixin(DensityLevelMixin):
    __lead_profiles: Sequence[LeadProfile] | None = None

    @overload
    def lead_profile(
        self, lead_profile: LeadProfile, /, *additional_profiles: LeadProfile
    ) -> Self: ...

    @overload
    def lead_profile(
        self,
        pitch: float,
        span: Toleranced | float,
        length: Toleranced | float,
        width: float | Toleranced,
        protrusion: LeadProtrusion,
    ) -> Self: ...

    def lead_profile(
        self,
        pitch: LeadProfile | float,
        span: float | Toleranced | LeadProfile = 0,
        length: float | Toleranced | LeadProfile = 0,
        width: float | Toleranced | LeadProfile = 0,
        protrusion: LeadProtrusion | None | LeadProfile = None,
        *additional_profiles: LeadProfile,
    ) -> Self:
        if isinstance(pitch, LeadProfile):
            lead_profiles = [pitch]
            if isinstance(span, LeadProfile):
                lead_profiles.append(span)
            if isinstance(length, LeadProfile):
                lead_profiles.append(length)
            if isinstance(width, LeadProfile):
                lead_profiles.append(width)
            if isinstance(protrusion, LeadProfile):
                lead_profiles.append(protrusion)
            if additional_profiles:
                lead_profiles.extend(additional_profiles)
        else:
            if not isinstance(span, Toleranced | float):
                raise TypeError("Span must be a float or Toleranced")
            if not isinstance(length, Toleranced | float):
                raise TypeError("Length must be a float or Toleranced")
            if not isinstance(width, Toleranced | float):
                raise TypeError("Width must be a float or Toleranced")
            if not isinstance(protrusion, LeadProtrusion | None):
                raise TypeError("Protrusion must be a LeadProtrusion")
            assert protrusion is not None
            lead_profile = LeadProfile(
                span=Toleranced.exact(span),
                pitch=pitch,
                type=SMDLead(
                    length=Toleranced.exact(length),
                    width=Toleranced.exact(width),
                    lead_type=protrusion,
                ),
            )
            lead_profiles = (lead_profile,)
        self.__lead_profiles = lead_profiles
        return self

    def _lead_profiles(self) -> Sequence[LeadProfile]:
        if self.__lead_profiles is None:
            raise ValueError("No lead profile specified")
        return self.__lead_profiles

    @property
    def _lead_profiles_optional(self) -> Sequence[LeadProfile] | None:
        return self.__lead_profiles

    def _lead_placements(self) -> Sequence[LeadPlacement]:
        profiles = self._lead_profiles()
        if profiles is None:
            raise ValueError("No lead profile specified")
        return tuple(p.compute_placements(self._density_level) for p in profiles)
