from __future__ import annotations
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import math
from types import EllipsisType
from typing import ClassVar, Self, override

from jitx.container import Composite
from jitx.context import Context
from jitx.feature import Cutout, Paste, Soldermask
from jitx.landpattern import Pad
from jitx.layerindex import Side
from jitx.shapes import Shape
from jitx.shapes.composites import bounds_area, bounds_dimensions, rectangle
from jitx.shapes.primitive import Circle, Empty
from jitx.shapes.shapely import ShapelyGeometry
from jitx.toleranced import Toleranced
from jitx.transform import Transform
import shapely

from . import LandpatternProvider, SoldermaskRegistrationContext
from .grid_layout import GridLayoutInterface, GridPosition
from .ipc import DensityLevel, DensityLevelContext

type PadFeatureConfig = float | Shape | ShapeAdjustment | None


class ShapeAdjustment:
    """Base class to be used in a :py:class:`PadConfig` to specify how to adjust a
    template shape to generate the shape for a specific feature (cutout,
    soldermask, paste, etc.)."""

    def adjust_shape(self, shape: Shape) -> Shape:
        raise NotImplementedError()


@dataclass(frozen=True)
class RelAdj(ShapeAdjustment):
    """Relative Adjustment Amount

    This class indicates a relative (proportional) amount to adjust the template
    shape for a pad by to generate the shape for a specific feature (cutout,
    soldermask, paste, etc.). A value of 0.0 indicates no adjustment, 1.0
    indicates a doubling in size, -0.5 indicates a halving in size.
    """

    amount: float
    """Relative adjustment amount"""

    def __post_init__(self):
        if self.amount <= -1.0:
            raise ValueError(
                f"Relative adjustment amount must be > -1.0: {self.amount}"
            )

    @override
    def adjust_shape(self, shape: Shape) -> Shape:
        """Adjust the shape by this relative adjustment amount

        Args:
            shape: the shape to adjust

        Returns:
            The adjusted shape
        """

        if isinstance(shape, Circle):
            return shape.__class__(diameter=shape.diameter * (1.0 + self.amount))
        else:
            shapely_shape = shape.to_shapely()
            bounds = shapely_shape.bounds
            min_dim = min(bounds_dimensions(bounds))
            adj = min_dim * (1.0 + self.amount)
            return shapely_shape.buffer(adj)


def _if_set[T](value: T | EllipsisType, otherwise: Callable[[], T]) -> T:
    if value is not ...:
        return value
    else:
        return otherwise()


def _if_set_c[T](value: T | EllipsisType, otherwise: T) -> T:
    if value is not ...:
        return value
    else:
        return otherwise


def _if_soldermask(soldermask: PadFeatureConfig | EllipsisType) -> PadFeatureConfig:
    if soldermask is not ...:
        return soldermask
    else:
        return SoldermaskRegistrationContext.get().soldermask_registration


def _if_density(density: DensityLevel | EllipsisType) -> DensityLevel:
    if density is not ...:
        return density
    else:
        return DensityLevelContext.get().density_level


def make_feature_shape(
    template: Shape | None,
    config: PadFeatureConfig,
) -> Shape | None:
    """Make a feature shape from a template and a pad feature configuration

    This function is used to create the shapes for the soldermask, paste, and
    cutout features of a pad.

    Args:
        template: the template shape to use
        config: the configuration to use

    Returns:
        The feature shape
    """

    if template is None:
        return None
    if isinstance(config, float | int):
        if config == 0:
            return template
        elif isinstance(template, Circle):
            return template.__class__(diameter=template.diameter + config)
        else:
            return template.to_shapely().buffer(
                config, cap_style="square", join_style="mitre"
            )
    else:
        match config:
            case Shape():
                return config
            case ShapeAdjustment():
                return config.adjust_shape(template)
            case None:
                return None
            case _:
                raise ValueError(f"Invalid pad feature config: {config}")


def smaller_shape(a: Shape | None, b: Shape | None) -> Shape | None:
    """Return the shape with the smaller bounding box area

    This function is used to determine the smaller of two shapes based on their
    bounding box area. If either shape is ``None``, the other shape is returned.
    If both shapes are ``None``, ``None`` is returned.

    Args:
        a: the first shape, or ``None``
        b: the second shape, or ``None``

    Returns:
        The shape with the smaller bounding box area, or ``None`` if both shapes
        are ``None``
    """

    match a, b:
        case None, None:
            return None
        case None, _:
            return b
        case _, None:
            return a
        case Circle(), Circle():
            return a if a.diameter <= b.diameter else b
        case Shape(), Shape():
            a_bounds = a.to_shapely().bounds
            b_bounds = b.to_shapely().bounds
            a_area = bounds_area(a_bounds)
            b_area = bounds_area(b_bounds)
            return a if a_area <= b_area else b
        case _:
            raise ValueError(
                f"Cannot call 'smaller_shape' with {type(a)} and {type(b)}"
            )


def copper_contains_cutout(copper: Shape | None, cutout: Shape | None) -> bool:
    """Check if a copper shape contains a cutout shape

    This function checks if a copper shape contains a cutout shape. If the
    cutout shape is ``None`` or an empty shape, this function returns ``True``.
    If the copper shape is ``None`` or an empty shape, this function returns
    ``False``.

    Args:
        copper: the copper shape
        cutout: the cutout shape

    Returns:
        ``True`` if the copper shape contains the cutout shape, ``False``
        otherwise
    """

    if cutout is None or isinstance(cutout, Empty):
        return True
    elif copper is None or isinstance(copper, Empty):
        return False
    elif isinstance(cutout, Circle) and isinstance(copper, Circle):
        return cutout.diameter < copper.diameter
    else:
        return copper.to_shapely().contains(cutout.to_shapely())


class SMDPad(Pad):
    """SMD Pad

    This class creates an SMD landpattern pad.
    By default, the soldermask shape is the copper shape expanded by the current
    design soldermask registration amount. The paste shape is the smaller of the
    copper and soldermask shapes.
    """

    soldermask: Soldermask | None = None
    """The soldermask shape for the pad"""

    paste: Paste | None = None
    """The paste shape for the pad"""

    def __init__(
        self,
        copper: Shape,
        *,
        soldermask: PadFeatureConfig | EllipsisType = ...,
        paste: PadFeatureConfig | EllipsisType = ...,
    ):
        """Initialize the SMD pad

        Args:
            copper: the copper shape
            soldermask: optional, the soldermask shape
                If not provided, the current design soldermask registration will
                be used to expand the copper shape to create the soldermask
            paste: optional, the paste shape
                If not provided, the smaller of the copper and soldermask shapes
                will be used
        """

        self.shape = copper
        soldermask = _if_soldermask(soldermask)
        soldermask_shape = make_feature_shape(copper, soldermask)
        if soldermask_shape is not None:
            self.soldermask = Soldermask(soldermask_shape)

        if paste is ...:
            paste_shape = smaller_shape(copper, soldermask_shape)
        else:
            paste_shape = make_feature_shape(copper, paste)
        if paste_shape is not None:
            self.paste = Paste(paste_shape)


class THPad(Pad):
    """Through-Hole Pad

    This class creates a through-hole landpattern pad.
    By default, the soldermask shape is the copper shape expanded by the current
    design soldermask registration amount, and no paste is generated.
    """

    cutout: Cutout | None = None
    """The cutout shape for the pad"""

    soldermask: Soldermask | None = None
    """The soldermask shape for the top side of the pad"""

    soldermask_bottom: Soldermask | None = None
    """The soldermask shape for the bottom side of the pad"""

    paste: Paste | None = None
    """The paste shape for the pad"""

    def __init__(
        self,
        copper: Shape,
        cutout: Shape,
        *,
        soldermask: PadFeatureConfig | EllipsisType = ...,
        paste: PadFeatureConfig = None,
    ):
        """Initialize the through-hole pad

        Args:
            copper: the copper shape
            cutout: the cutout shape
            soldermask: optional, the soldermask shape configuration
                If not provided, the current design soldermask registration will
                be used to expand the copper shape to create the soldermask
            paste: optional, the paste shape configuration
                If not provided, no paste will be generated
        """

        if not copper_contains_cutout(copper, cutout):
            raise ValueError(
                f"Cutout shape is not fully contained in copper pad shape: cutout={cutout} copper={copper}"
            )
        self.shape = copper
        self.cutout = Cutout(cutout)
        soldermask = _if_soldermask(soldermask)
        soldermask_shape = make_feature_shape(copper, soldermask)
        if soldermask_shape is not None:
            self.soldermask = Soldermask(soldermask_shape, Side.Top)
            self.soldermask_bottom = Soldermask(soldermask_shape, Side.Bottom)

        paste_shape = make_feature_shape(copper, paste)
        if paste_shape is not None:
            self.paste = Paste(paste_shape)


class NPTHPad(Composite):
    """Non-Plated Through-Hole "Pad"

    This class creates a non-plated through-hole landpattern object. Since
    :py:class:`~jitx.landpattern.Pad` implies a possible connection with a
    :py:class:`~jitx.net.Port` and requires a copper shape, this class is not
    actually a :py:class:`~jitx.landpattern.Pad`, but rather a subclass of
    :py:class:`~jitx.container.Composite` instead and will just generate a hole
    in the landpattern that can't be connected.
    """

    cutout: Cutout
    """The cutout shape for the pad"""

    soldermask: Soldermask | None = None
    """The soldermask shape for the top side of the pad"""

    soldermask_bottom: Soldermask | None = None
    """The soldermask shape for the bottom side of the pad"""

    def __init__(
        self,
        cutout: Shape,
        *,
        soldermask: PadFeatureConfig | EllipsisType = ...,
    ):
        """Initialize the non-plated through-hole pad

        Args:
            cutout: The shape of the cutout for the pad
            soldermask: Configuration for the soldermask shape of the pad.
                If a :py:class:`Shape` is provided, it will be used directly.
                If a `float` or if a py:class:`ShapeAdjustment`, such as
                :py:class:`RelAdj`, is provided, it will be used to adjust the
                soldermask shape. If no configuration is provided, the current
                design soldermask registration amount will be used.
        """

        self.cutout = Cutout(cutout)
        soldermask = _if_soldermask(soldermask)
        soldermask_shape = make_feature_shape(cutout, soldermask)
        if soldermask_shape is not None:
            self.soldermask = Soldermask(soldermask_shape, Side.Top)
            self.soldermask_bottom = Soldermask(soldermask_shape, Side.Bottom)


class PadConfig:
    """Pad Configuration

    This abstract class defines an interface for classes to specify how pads
    should be constructed from a template shape.
    """

    def make_pad(self, template: Shape) -> Pad:
        raise NotImplementedError()


@dataclass(frozen=True)
class SMDPadConfig(PadConfig):
    """SMD Pad Configuration

    This class specifies how the feature shapes for an SMD pad should be
    constructed from a template shape.
    The default behaviors are:
    - copper = match template
    - soldermask = expand template by the design soldermask registration amount
    - paste = smaller of copper or soldermask
    """

    copper: PadFeatureConfig | EllipsisType = ...
    """The copper shape configuration"""

    soldermask: PadFeatureConfig | EllipsisType = ...
    """The soldermask shape configuration"""

    paste: PadFeatureConfig | EllipsisType = ...
    """The paste shape configuration"""

    def make_pad(self, template: Shape) -> SMDPad:
        """Make an SMD pad from a template shape

        Args:
            template: the template shape

        Returns:
            The SMD pad
        """

        copper = make_feature_shape(template, _if_set_c(self.copper, 0.0))
        soldermask = make_feature_shape(template, _if_soldermask(self.soldermask))
        paste = make_feature_shape(
            template, _if_set(self.paste, lambda: smaller_shape(copper, soldermask))
        )

        if copper is None:
            copper = Empty()
        return SMDPad(copper, soldermask=soldermask, paste=paste)


@dataclass(frozen=True)
class THPadConfig(PadConfig):
    """Through-Hole Pad Configuration

    This class specifies how the feature shapes for a through-hole pad should be
    constructed from a template shape.
    The default behaviors are:
    - copper = match template
    - cutout = match template
    - soldermask = expand copper by the design soldermask registration amount
    - paste = do not generate
    """

    copper: PadFeatureConfig | EllipsisType = ...
    """The copper shape configuration"""

    cutout: PadFeatureConfig | EllipsisType = ...
    """The cutout shape configuration"""

    soldermask: PadFeatureConfig | EllipsisType = ...
    """The soldermask shape configuration"""

    paste: PadFeatureConfig | EllipsisType = ...
    """The paste shape configuration"""

    def make_pad(self, template: Shape) -> THPad:
        """Make a through-hole pad from a template shape

        Args:
            template: the template shape

        Returns:
            The through-hole pad
        """

        copper = make_feature_shape(template, _if_set_c(self.copper, 0.0))
        cutout = make_feature_shape(template, _if_set_c(self.cutout, 0.0))
        assert copper_contains_cutout(copper, cutout), (
            f"Cutout shape is not fully contained in copper pad shape: cutout={cutout} copper={copper}"
        )
        soldermask = make_feature_shape(copper, _if_soldermask(self.soldermask))
        paste = make_feature_shape(copper, _if_set_c(self.paste, None))

        if copper is None:
            copper = Empty()
        if cutout is None:
            cutout = Empty()
        return THPad(copper, cutout=cutout, soldermask=soldermask, paste=paste)


@dataclass(frozen=True)
class IPCTHPadConfig(PadConfig):
    """IPC Through-Hole Pad Configuration

    This class uses the IPC-2222 standard for calculating through-hole pad and
    hole sizes based on the lead diameter.
    The default behaviors are:
    - copper = based on IPC-2222
    - cutout = based on IPC-2222
    - soldermask = expand copper by the design soldermask registration amount
    - paste = do not generate
    """

    copper: PadFeatureConfig | EllipsisType = ...
    """The copper shape configuration"""

    cutout: PadFeatureConfig | EllipsisType = ...
    """The cutout shape configuration"""

    soldermask: PadFeatureConfig | EllipsisType = ...
    """The soldermask shape configuration"""

    paste: PadFeatureConfig | EllipsisType = ...
    """The paste shape configuration"""

    density_level: DensityLevel | EllipsisType = ...
    """The density level to use for IPC calculations"""

    def make_pad(self, template: Shape) -> THPad:
        """Make an IPC through-hole pad from a template shape

        Args:
            template: the template shape

        Returns:
            The IPC through-hole pad
        """

        if isinstance(template, Circle):
            lead_diameter = template.diameter
        else:
            # approximate lead diameter as diagonal length of bounding box
            bounds = template.to_shapely().bounds
            lead_diameter = math.hypot(*bounds_dimensions(bounds))
        density_level = self.density_level
        if density_level is None:
            density_level = DensityLevelContext.get().density_level
        hole_diam, pad_diam = compute_hole_and_pad_diameters(
            Toleranced.exact(lead_diameter), _if_density(density_level)
        )

        copper = make_feature_shape(
            template, _if_set(self.copper, lambda: Circle(diameter=pad_diam))
        )
        cutout = make_feature_shape(
            template, _if_set(self.cutout, lambda: Circle(diameter=hole_diam))
        )
        assert copper_contains_cutout(copper, cutout), (
            f"Cutout shape is not fully contained in copper pad shape: cutout={cutout} copper={copper}"
        )
        soldermask = make_feature_shape(copper, _if_soldermask(self.soldermask))
        paste = make_feature_shape(copper, _if_set_c(self.paste, None))

        if copper is None:
            copper = Empty()
        if cutout is None:
            cutout = Empty()
        return THPad(copper, cutout=cutout, soldermask=soldermask, paste=paste)


# More info on IPC-2222
# https://www.pcblibraries.com/forum/ipc2221-2222-and-throughhole-pad-stacks_topic2586.html#:~:text=typical%20hole%20size


@dataclass(frozen=True)
class ThroughHolePadConfigurationContext(Context):
    """Configuration for through-hole pad generation. The default values can be
    overridden by declaring this context in your design hierarchy; the values
    will then be used for anything generated beneath that point.

    >>> class MyCircuit(Circuit):
    ...     th_settings = ThroughHolePadConfigurationContext(
    ...         min_outer_layer_pad_size=0.4
    ...     )
    """

    _global_default: ClassVar[ThroughHolePadConfigurationContext]

    min_outer_layer_pad_size: float = 0.2032
    """The minimum size of a circular pad on the outer layers"""
    max_hole_size_tolerance: float = 0.0508
    """The tolerance on the diameter of a hole of the largest size"""
    min_hole_size_tolerance: float = 0.0508
    """The tolerance on the diameter of a hole of the smallest size"""
    hole_position_tolerance: float = 0.0508
    """The tolerance on placing any hole"""
    hole_to_lead_tolerance: Mapping[DensityLevel, tuple[float, float]] = field(
        default_factory=lambda: {
            DensityLevel.A: (0.70, 0.25),
            DensityLevel.B: (0.70, 0.20),
            DensityLevel.C: (0.60, 0.15),
        }
    )
    """IPC 2222 Table 9-3"""

    @classmethod
    def get(cls) -> ThroughHolePadConfigurationContext:
        return super().get() or cls._global_default


# Ensure that we use the same object instance for the default, or it'll
# register as a separate dependency if used in memoization.
ThroughHolePadConfigurationContext._global_default = (
    ThroughHolePadConfigurationContext()
)


def compute_hole_diameter(
    lead_diameter: Toleranced, density_level: DensityLevel
) -> float:
    """Compute the hole diameter for a through-hole pad based on IPC 2222
    rules.

    Args:
        lead_diameter: Size of the lead for this hole. This should be the
            overall diameter of the lead, ie, for a square lead this diameter is
            the diagonal measurement of the square.
        density_level: IPC density level for board manufacturing

    Returns:
        The hole diameter in mm.
    """
    conf = ThroughHolePadConfigurationContext.require()
    max_h2l, min_h2l = conf.hole_to_lead_tolerance[density_level]

    # Hole size is average of min and max possible sizes
    # given the design rules.
    max_hole_diam = lead_diameter.min_value - conf.max_hole_size_tolerance + max_h2l
    min_hole_diam = lead_diameter.max_value + conf.min_hole_size_tolerance + min_h2l

    return 0.5 * (max_hole_diam + min_hole_diam)


class THPadAdjustment(ShapeAdjustment):
    """Adjustment Amount for Through-Hole Pads given the hole shape as
    template, and can be used as a :py:class:`THPadConfig` copper adjustment,
    in particular if :py:class:`IPCTHPadConfig` is not appropriate.

    >>> THPadConfig(copper=THPadAdjustment())
    """

    def adjust_shape(self, shape: Shape) -> Shape:
        if isinstance(shape, Circle):
            return Circle(diameter=compute_pad_diameter(shape.diameter))
        else:
            # approximate lead diameter as diagonal length of bounding box
            bounds = shape.to_shapely().bounds
            diameter = math.hypot(*bounds_dimensions(bounds))
            return Circle(diameter=compute_pad_diameter(diameter))


def compute_pad_diameter(
    hole_diameter: float,
) -> float:
    """Compute the pad diameter for a through-hole pad based on IPC 2222
    rules.

    Args:
        hole_diameter: Size of the hole for this pad.

    Returns:
        The pad diameter in mm.
    """
    conf = ThroughHolePadConfigurationContext.require()
    return hole_diameter + max(
        conf.max_hole_size_tolerance + 0.5,
        conf.max_hole_size_tolerance + conf.hole_position_tolerance + 50.0e-6,
        conf.min_outer_layer_pad_size,
    )


def compute_hole_and_pad_diameters(
    lead_diameter: Toleranced, density_level: DensityLevel
) -> tuple[float, float]:
    """Compute the hole and pad diameters for a through-hole pad based on IPC
    2222 rules.

    Args:
        lead_diameter: Size of the lead for this hole. This should be the
            overall diameter of the lead, ie, for a square lead this diameter is
            the diagonal measurement of the square.
        density_level: IPC density level for board manufacturing

    Returns:
        A tuple of (hole diameter, pad diameter) in mm.
    """
    hole_diam = compute_hole_diameter(lead_diameter, density_level)
    pad_diam = compute_pad_diameter(hole_diam)

    return hole_diam, pad_diam


class PadConfigurationMixin:
    __pad_config: PadConfig | None = None

    def pad_config(self, pad_config: PadConfig) -> Self:
        self.__pad_config = pad_config
        return self

    def _pad_config(self) -> PadConfig:
        if self.__pad_config is None:
            raise ValueError("No pad configuration specified")
        return self.__pad_config

    @property
    def _pad_config_optional(self) -> PadConfig | None:
        return self.__pad_config


class GridPadShapeGenerator:
    def pad_shape(self, pos: GridPosition) -> Shape:
        raise ValueError("No pad shape specified")


class FixedPadShapeGenerator(GridPadShapeGenerator):
    def __init__(self, shape: Shape):
        self.__shape = shape

    def pad_shape(self, pos: GridPosition) -> Shape:
        return self.__shape


class PadShapeProvider:
    """Sub-classes of this can be mixed in to provide a pad shape override for a specific
    grid position. It is not intended to be used for all pads, use a pad shape
    generator through :py:class:`GridPadShapeGeneratorMixin` for that."""

    def _pad_shape(self, pos: GridPosition) -> Shape:
        raise ValueError("No pad shape specified")


class GridPadShapeGeneratorMixin(
    PadConfigurationMixin, PadShapeProvider, GridLayoutInterface
):
    __pad_shape_generator: GridPadShapeGenerator | None = None

    def pad_shape_generator(self, pad_shape_generator: GridPadShapeGenerator) -> Self:
        """Use a generator to create pad shapes based on grid position"""
        self.__pad_shape_generator = pad_shape_generator
        return self

    def pad_shape(self, shape: Shape) -> Self:
        """Set a fixed pad shape for all pads in the landpattern"""
        self.__pad_shape_generator = FixedPadShapeGenerator(shape)
        return self

    @override
    def _pad_shape(self, pos: GridPosition) -> Shape:
        pads = self.__pad_shape_generator
        if pads is None:
            return super()._pad_shape(pos)
        return pads.pad_shape(pos)

    def _create_pad(self, pos: GridPosition) -> Pad:
        return self._pad_config().make_pad(self._pad_shape(pos)).at(pos.pose)


class ThermalPadGeneratorMixin(PadConfigurationMixin, LandpatternProvider):
    """Mixin to allow adding a separate thermal pad to the landpattern"""

    __shape: Shape | None = None
    __config: SMDPadConfig | None = None
    thermal_pads: list[Pad]
    """The generated thermal pad. It can be referenced in a
    :py:class:`jitx.landpattern.PadMapping` to map a port to it."""

    def thermal_pad(self, shape: Shape, config: SMDPadConfig | None = None) -> Self:
        """Set the thermal pad for the landpattern, with optional configuration to control the pad features.

        Args:
            shape: The shape of the thermal pad
            config: Optional configuration to control the pad features. If not
                provided, the default :py:class:`SMDPadConfig` will be used.
        """
        self.__shape = shape
        self.__config = config
        return self

    @override
    def _build(self):
        if hasattr(self, "thermal_pads"):
            del self.thermal_pads
        super()._build()

    @override
    def _build_decorate(self):
        super()._build_decorate()

        if self.__shape is None:
            return
        shape = self.__shape
        config = self.__config or self._pad_config_optional or SMDPadConfig()
        self.thermal_pads = [config.make_pad(shape).at(0, 0)]


@dataclass
class WindowSubdivide(ShapeAdjustment):
    """This class generates a windowed grid adjustment to a pad shape, ideal
    for paste applications. For example, you might use this for generating a
    large thermal pad for a QFN where you do not want the entire pad to be
    covered in paste.
    """

    padding: float | tuple[float, float] = 0.25  # mm
    """Pad distance between copper and window edge

    Sets the buffer distance between window openings and between the edge of
    copper to the window opening. If this is a tuple, the first element is the
    horizontal buffer distance and the second element is the vertical buffer
    distance. The default is 0.25.
    """
    gridShape: tuple[int, int] = 2, 2
    """ Window grid dimensions

    Dimensions of the grid of window openings. By default this uses a 2 x 2
    grid.
    """

    def generate_window(self, w: float, h: float) -> Shape:
        """Generate the window opening shape.

        By default, this generates a rectangle.

        Args:
            w: width of the window
            h: height of the window

        Returns:
            The window opening shape
        """

        return rectangle(w, h)

    @override
    def adjust_shape(self, shape: Shape) -> Shape:
        """Generate the paste application

        Args:
            copper: shape of the copper pad that this paste will be applied to

        Returns:
            The paste application shape
        """

        padding = self.padding
        if not isinstance(padding, tuple):
            padding = (padding, padding)
        padX, padY = padding
        cu = shape.to_shapely()

        cuMinX, cuMinY, cuMaxX, cuMaxY = cu.bounds
        cuW = cuMaxX - cuMinX
        cuH = cuMaxY - cuMinY

        cu = cu.buffer(-min(padX, padY))
        gX, gY = self.gridShape

        numPadX = 2 + (gX - 1)
        numPadY = 2 + (gY - 1)
        availW = cuW - (numPadX * padX)
        availH = cuH - (numPadY * padY)

        if availW < 0.0 or availH < 0:
            raise ValueError(
                f"Padding is too large for this grid size: available W={availW} H={availH} "
            )

        pW = availW / gX
        pH = availH / gY

        window = self.generate_window(pW, pH)
        # window = rectangle(pW,pH)

        # TODO - we need to check that the paste opening is larger
        #   than the minimum required size based on the rules.

        def compute_positions():
            for y in range(gY):
                ycoord = y * (pH + padY)
                for x in range(gX):
                    xcoord = x * (pW + padX)
                    yield Transform.translate(xcoord, ycoord)

        totalW = (numPadX * padX) + (gX * pW)
        totalH = (numPadY * padY) + (gY * pH)
        offX = (totalW / 2) - (padX + pW / 2)
        offY = (totalH / 2) - (padY + pH / 2)

        ctrTx = Transform.translate(-offX, -offY)

        def compute_windows():
            for posTx in compute_positions():
                elem = ctrTx * posTx * window
                yield elem.to_shapely()

        allWindows = ShapelyGeometry(
            shapely.unary_union([x.g for x in compute_windows()]).intersection(cu.g)
        )
        return allWindows
