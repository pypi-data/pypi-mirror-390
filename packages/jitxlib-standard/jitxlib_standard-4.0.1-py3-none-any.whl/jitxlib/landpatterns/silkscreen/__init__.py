from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self, cast

from jitx._structural import Structurable
from jitx.context import Context
import jitx

from .. import ApplyToMixin as ApplyToMixin


class _SilkscreenSoldermaskDefault:
    @property
    def clearance(self) -> float:
        return jitx.current.substrate.constraints.min_silk_solder_mask_space


@dataclass(frozen=True)
class SilkscreenSoldermaskClearanceContext(Context):
    _global_default: ClassVar[_SilkscreenSoldermaskDefault] = (
        _SilkscreenSoldermaskDefault()
    )
    clearance: float

    @classmethod
    def get(cls) -> SilkscreenSoldermaskClearanceContext:
        """Get the current silkscreen soldermask clearance context. If unset it defaults to the
        minimum clearance specified by the substrate."""
        # pretend it's a context even though it's practically mutable, the
        # lookup on the substrate will still make the correct context based
        # memoization.
        return super().get() or cast(
            SilkscreenSoldermaskClearanceContext, cls._global_default
        )


class SilkscreenSoldermaskClearanceMixin(Structurable):
    __clearance: float | None = None
    __clearance_ctx: float

    if not TYPE_CHECKING:

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__clearance_ctx = SilkscreenSoldermaskClearanceContext.get().clearance

    def silkscreen_soldermask_clearance(self, clearance: float) -> Self:
        self.__clearance = clearance
        return self

    @property
    def _silkscreen_soldermask_clearance(self) -> float:
        return self.__clearance or self.__clearance_ctx
