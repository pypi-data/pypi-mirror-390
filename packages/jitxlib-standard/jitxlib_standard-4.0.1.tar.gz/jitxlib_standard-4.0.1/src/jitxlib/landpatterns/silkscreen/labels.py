from collections.abc import Callable
from typing import Self
from jitx import current
from jitx.anchor import Anchor
from jitx.feature import Silkscreen, Soldermask, Feature, Custom, Courtyard
from jitx.inspect import decompose
from jitx.shapes import Shape
from jitx.shapes.composites import Bounds
from jitx.shapes.primitive import Text
from jitx.substrate import FabricationConstraints
from . import ApplyToMixin
from .. import LandpatternProvider, LineWidthMixin


class TextPlacerMixin(LineWidthMixin):
    def _compute_text(
        self,
        string: str,
        placement: Anchor,
        bounds: Bounds,
        size: float | None,
        margin: float | None,
    ):
        x, y = placement.to_point(bounds)

        if margin is None:
            margin = 2 * self._line_width

        match placement.vertical():
            case Anchor.N:
                y += margin
            case Anchor.S:
                y -= margin
            case _:
                match placement.horizontal():
                    case Anchor.W:
                        x += margin
                    case Anchor.E:
                        x -= margin

        match placement:
            case Anchor.N:
                anchor = Anchor.S
            case Anchor.S:
                anchor = Anchor.N
            case Anchor.W:
                anchor = Anchor.E
            case Anchor.E:
                anchor = Anchor.W
            case Anchor.NE:
                anchor = Anchor.SE
            case Anchor.NW:
                anchor = Anchor.SW
            case Anchor.SE:
                anchor = Anchor.NE
            case Anchor.SW:
                anchor = Anchor.NW
            case _:
                anchor = Anchor.C

        fab, *_ = decompose(current.substrate, FabricationConstraints)
        size = max(size or 0, fab.min_silkscreen_text_height)
        return Text(string, size, anchor).at(x, y)


class ReferenceDesignatorMixin(ApplyToMixin, TextPlacerMixin, LandpatternProvider):
    __placement: Anchor | None = Anchor.SW
    __margin: float | None = None
    __size: float | None = None

    def reference_designator(
        self,
        placement: Anchor | None,
        *,
        margin: float | None = None,
        size: float | None = None,
    ) -> Self:
        """Set the placement of the reference designator. The default placement
        is :py:attr:`~jitx.anchor.Anchor.SW`.

        Args:
            placement: The placement of the reference designator. If ``None``, the
                reference designator will be removed.
            margin: The margin between the reference designator and the
                soldermask. If None, a default margin will be used based on the
                current line width.
            size: The text size of the reference designator, limited by the
                current fabrication constraints. If ``None``, the size will
                be set to the minimum permissible size.
        """
        self.__placement = placement
        self.__margin = margin
        self.__size = size
        return self

    def _build_decorate(self):
        super()._build_decorate()

        if self.__placement is not None:
            bounds = self._applies_to_bounds((Soldermask, Courtyard))
            self._reference_designator = Silkscreen(
                self._compute_text(
                    ">REF", self.__placement, bounds, self.__size, self.__margin
                )
            )


class ValueLabelMixin(ApplyToMixin, TextPlacerMixin, LandpatternProvider):
    __placement: Anchor | None = None
    __margin: float | None = None
    __size: float | None = None
    __feature: Callable[[Shape], Feature]

    def value_label(
        self,
        placement: Anchor | None = Anchor.SE,
        *,
        margin: float | None = None,
        size: float | None = None,
        layer: Callable[[Shape], Feature] | None = None,
    ) -> Self:
        """Enable the placement of a value label.

        Args:
            placement: The placement of the value label. If ``None``, the value
                label will be removed.
            margin: The margin between the value label and the soldermask. If
                None, a default margin will be used based on the current line
                width.
            size: The text size of the value label, limited by the current
                fabrication constraints. If ``None``, the size will be set to
                the minimum permissible size.
            layer: The layer to place the text on, e.g.
                :py:class:`jitx.feature.Silkscreen`. If ``None``, the text will
                be placed on a custom layer named "Component Values".
        """
        self.__placement = placement
        self.__margin = margin
        self.__size = size
        if layer is not None:
            self.__feature = layer
        else:
            self.__feature = lambda s: Custom(s, name="Component Values")
        return self

    def _build_decorate(self):
        super()._build_decorate()

        if self.__placement is not None:
            bounds = self._applies_to_bounds((Soldermask, Courtyard))
            self._value_label = self.__feature(
                self._compute_text(
                    ">VALUE", self.__placement, bounds, self.__size, self.__margin
                )
            )
