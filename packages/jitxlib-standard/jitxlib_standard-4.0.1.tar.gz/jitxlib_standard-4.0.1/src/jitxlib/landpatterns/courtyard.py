from __future__ import annotations
from typing import override

from jitx.shapes import Shape

from .package import PackageBodyMixin
from . import ApplyToMixin, LandpatternGenerator, LandpatternProvider, LineWidthMixin
from .leads import LeadProfileMixin
from .ipc import DensityLevel, DensityLevelMixin
from .leads import LeadProfile

from jitx.feature import Feature, Custom, Soldermask, Courtyard
from jitx.shapes.composites import (
    bounds_area,
    bounds_dimensions,
    buffer_bounds,
    plus_symbol,
    rectangle_from_bounds,
)


class CourtyardGenerator:
    def make_courtyard(self, target: CourtyardGeneratorMixin) -> Courtyard:
        raise NotImplementedError(f"{self.__class__.__name__}.make_courtyard")


class CourtyardGeneratorMixin(
    ApplyToMixin,
    PackageBodyMixin,
    LeadProfileMixin,
    DensityLevelMixin,
    LandpatternProvider,
):
    __generator: CourtyardGenerator | None = None
    _courtyard: Courtyard | None = None

    def courtyard(self, generator: CourtyardGenerator):
        """Add a courtyard generator to the landpattern"""
        self.__generator = generator
        return self

    @override
    def _build(self):
        # clear out so it's not discovered by others mixins for the first time
        # on the second run
        self._courtyard = None
        super()._build()

    @override
    def _build_decorate(self):
        super()._build_decorate()
        if self.__generator is not None:
            self._courtyard = self.__generator.make_courtyard(self)


class OriginMarkerMixin(ApplyToMixin, LineWidthMixin, LandpatternProvider):
    __size: float = 1
    __ratio: float = 0.5

    _origin_marker: Feature | None = None

    def origin_marker(
        self, max_size: float | None = None, max_ratio: float | None = None
    ):
        if max_size is not None:
            self.__size = max_size
        if max_ratio is not None:
            self.__ratio = max_ratio
        return self

    @override
    def _build(self):
        self._origin_marker = None
        super()._build()

    @override
    def _build_decorate(self):
        super()._build_decorate()
        line_width = self._line_width
        size = self.__size
        ratio = self.__ratio
        bounds = self._applies_to_bounds(Soldermask)
        w, h = bounds_dimensions(bounds)
        lower_dim = min(w, h)
        size = min(size, lower_dim * ratio)
        plus_shape = plus_symbol(length=size, line_width=line_width)
        self._origin_marker = Custom(shape=plus_shape, name="Origin")


def courtyard_excess(density_level: DensityLevel) -> float:
    """Compute the courtyard excess for a density level

    Values are taken from IPC-7351B Table 3-17.

    Args:
        density_level: the density level to compute the courtyard excess for

    Return:
        the courtyard excess (buffer distance from pad features to courtyard
        shape) based on the density level.
    """

    match density_level:
        case DensityLevel.A:
            return 2.0
        case DensityLevel.B:
            return 1.0
        case DensityLevel.C:
            return 0.5


def lead_profile_courtyard_excess(
    lead_profile: LeadProfile,
    density_level: DensityLevel,
) -> float:
    """Compute the courtyard excess for a lead profile

    Args:
        lead_profile: the lead profile to compute the courtyard excess for
        density_level: the density level to compute the courtyard excess for

    Returns:
        the courtyard excess based on the lead profile and density level.
    """

    lead_type = lead_profile.type.lead_type
    return lead_type.fillets[density_level].courtyard_excess


class ExcessCourtyardGenerator(CourtyardGenerator):
    def __init__(self, excess: float | None = None):
        self.__excess = excess

    def __pick_excess(self, target: CourtyardGeneratorMixin):
        if self.__excess is not None:
            return self.__excess
        density_level = target._density_level
        lead_profiles = target._lead_profiles_optional
        if lead_profiles:
            return max(
                lead_profile_courtyard_excess(lp, density_level) for lp in lead_profiles
            )
        return courtyard_excess(density_level)

    def make_courtyard(self, target: CourtyardGeneratorMixin):
        extra: Shape | None = None
        pb = target._package_body_optional
        if pb:
            extra = pb.envelope(target._density_level)
        bounds = target._applies_to_bounds(Soldermask, additional=extra)
        excess = self.__pick_excess(target)
        if bounds_area(bounds) <= 0.0:
            raise ValueError("Feature bounds are empty")
        ctyd_shape = rectangle_from_bounds(buffer_bounds(bounds, excess))
        return Courtyard(ctyd_shape)


class ExcessCourtyard(CourtyardGeneratorMixin, LandpatternGenerator):
    """A courtyard generator mixin with a default ExcessCourtyard generator."""

    @override
    def __base_init__(self):
        super().__base_init__()
        self.courtyard(ExcessCourtyardGenerator())
