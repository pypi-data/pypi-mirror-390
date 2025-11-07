from collections.abc import Iterable
from typing import override

from jitx.shapes import Shape
from jitx.shapes.composites import plus_symbol
from jitx.shapes.primitive import Circle, Polygon
from jitx.shapes.shapely import ShapelyGeometry
from jitx.toleranced import Toleranced
from jitx.transform import Transform

from .. import LandpatternGenerator
from ..courtyard import ExcessCourtyard
from ..grid_layout import GridPosition, LinearNumbering
from ..ipc import DensityLevel
from ..leads import THLead
from ..pads import GridPadShapeGeneratorMixin, IPCTHPadConfig
from ..silkscreen.outlines import OutlineGenerator, SilkscreenOutline
from .smt import CathodeAnodeNumbering


# Minimum size of the silkscreen plus symbol polarity marker
MIN_PLUS_SIZE = 0.75
# Minimum height of the silkscreen triangle polarity marker
MIN_TRI_HEIGHT = 0.5


class RadialTwoPinBase(GridPadShapeGeneratorMixin, LandpatternGenerator):
    _num_rows: int = 2
    _num_cols: int = 1

    __lead: THLead
    __lead_spacing: Toleranced

    def __init__(self, lead: THLead, lead_spacing: Toleranced):
        super().__init__()
        self.pad_config(IPCTHPadConfig())
        self.__lead = lead
        self.__lead_spacing = lead_spacing

    def _pad_shape(self, pos: GridPosition) -> Shape:
        return Circle(diameter=self.__lead.width.typ)

    @override
    def _generate_layout(self) -> Iterable[GridPosition]:
        half_spacing = self.__lead_spacing.typ / 2
        return (
            GridPosition(0, 0, Transform.translate(0.0, half_spacing)),
            GridPosition(1, 0, Transform.translate(0.0, -half_spacing)),
        )


class RadialOutline(OutlineGenerator):
    def __init__(self, polarized: bool = False):
        super().__init__()
        self.__polarized = polarized

    @classmethod
    def plus_size_ratio(cls, density_level: DensityLevel) -> float:
        match density_level:
            case DensityLevel.A:
                return 0.25
            case DensityLevel.B:
                return 0.20
            case DensityLevel.C:
                return 0.15

    @override
    def make_shape(self, target: SilkscreenOutline) -> Shape:
        line_width = self._line_width(target)
        clearance = target._silkscreen_soldermask_clearance
        pb = target._package_body()
        dl = target._density_level
        envelope = pb.envelope(dl).to_shapely()
        outline = envelope.buffer(clearance + line_width / 2).boundary.buffer(
            line_width / 2
        )
        if self.__polarized:
            minx, miny, maxx, maxy = envelope.bounds
            h2 = (maxy - miny) / 2 + clearance + line_width
            width = maxx - minx

            plus_size_ratio = self.plus_size_ratio(dl)
            plus_len = max(MIN_PLUS_SIZE, plus_size_ratio * width)
            plus_y = (
                h2 + plus_len / 2.0 + 1.5 * line_width
            )  # 0.5 for the plus' line cap
            plus_shape = Transform.translate(0.0, plus_y) * plus_symbol(
                plus_len, line_width
            )

            # psr = self.plus_size_ratio(target._density_level)
            thickness = 2.5 * line_width
            height = h2 + thickness
            base = height * 0.5
            tri = Polygon(
                elements=[(0.0, 0.0), (-base, -height), (base, -height)]
            ).to_shapely()

            thickcl = clearance + line_width + thickness / 2
            thick = envelope.buffer(thickcl).boundary.buffer(thickness / 2)
            outline = outline.union(thick.intersection(tri.g)).union(
                plus_shape.to_shapely().g
            )
        return ShapelyGeometry(outline)


class RadialTwoPinDecorated(SilkscreenOutline, ExcessCourtyard, RadialTwoPinBase):
    def __base_init__(self):
        super().__base_init__()
        self.silkscreen_outline(RadialOutline())


class PolarizedRadialTwoPin(CathodeAnodeNumbering, RadialTwoPinDecorated):
    def __base_init__(self):
        super().__base_init__()
        self.silkscreen_outline(RadialOutline(polarized=True))


class RadialTwoPin(LinearNumbering, RadialTwoPinDecorated):
    pass
