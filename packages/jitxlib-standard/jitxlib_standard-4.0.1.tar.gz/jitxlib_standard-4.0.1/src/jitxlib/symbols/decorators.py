"""
Pin decorators module for JITX Standard Library

This module provides pin decorator definitions for use with symbol pins.
Decorators are collections of artwork that can be attached to pins to indicate
special properties like active-low signals, open-collector outputs, clock inputs,
and pin cardinality (input/output/bidirectional).
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field

from jitx.net import Port
from jitx.property import Property
from jitx.shapes import Shape
from jitx.shapes.primitive import Polygon, Circle, Polyline
from jitx.symbol import Direction
from jitx.transform import Point, Transform
from .common import DEF_LINE_WIDTH


# Decorator placement constants
class DecoratorPlacement(Enum):
    """
    Placement reference for pin decorators

    Indicates whether the decorator is placed inside or outside the box symbol.
    """

    OUTSIDE = "outside"
    INSIDE = "inside"


class OpenCollectorType(Enum):
    """
    Open collector output types

    Defines whether the open collector is a low-side sink (NPN/NMOS) or
    high-side source (PNP/PMOS).
    """

    SINK = "sink"
    """Low side open collector (NPN BJT or NMOS FET)"""
    SOURCE = "source"
    """High side open collector (PNP BJT or PMOS FET)"""


class CardinalityType(Enum):
    """
    Pin cardinality types

    Defines the direction of signal flow for pin decorators.
    """

    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"


# Active-Low decorator constants
DEF_ACTIVE_LOW_DIAM = 0.7
DEF_ACTIVE_LOW_NUDGE = (0.0, 0.0)

# Open-Collector decorator constants
DEF_OC_DEC_SIZE = 0.7
DEF_OC_TYPE = OpenCollectorType.SINK
DEF_OC_PULL = False

# Clock decorator constants
DEF_CLOCK_SIZE = 0.85

# Cardinality decorator constants
DEF_CARD_SIZE = (0.85, 0.85)


@dataclass
class DecoratorSpec:
    """
    Base class for all pin decorator specifications

    This is the base type for data structures that specify how pins should be decorated
    (e.g., Cardinality, ActiveLow, etc.)
    """

    def shapes(self) -> tuple[Shape, ...]:
        """Return the shapes that make up this decorator"""
        raise NotImplementedError("Subclasses must implement shapes()")

    def placement(self) -> DecoratorPlacement:
        """Return the placement type for this decorator"""
        raise NotImplementedError("Subclasses must implement placement()")


# Not yet supported
@dataclass
class DecoratorConfig:
    """Default configurations for all decorator types"""

    cardinality: Cardinality = field(
        default_factory=lambda: Cardinality(
            cardinality=CardinalityType.BIDIRECTIONAL,
            size=DEF_CARD_SIZE,
            nudge=None,
        )
    )
    """Configuration for cardinality decorators"""
    active_low: ActiveLow = field(
        default_factory=lambda: ActiveLow(
            diameter=DEF_ACTIVE_LOW_DIAM,
            nudge=DEF_ACTIVE_LOW_NUDGE,
        )
    )
    """Configuration for active-low decorators"""
    open_collector: OpenCollector = field(
        default_factory=lambda: OpenCollector(
            width=DEF_OC_DEC_SIZE,
            line_width=DEF_LINE_WIDTH,
            oc_type=DEF_OC_TYPE,
            pullup_down=DEF_OC_PULL,
        )
    )
    """Configuration for open-collector decorators"""
    clock: Clock = field(
        default_factory=lambda: Clock(
            size=DEF_CLOCK_SIZE,
            line_width=DEF_LINE_WIDTH,
        )
    )
    """Configuration for clock decorators"""


@dataclass
class PinDecorator(Property):
    """
    Pin decorator property. This should be assigned to a component port for
    pin-specific decoration.
    """

    spec: DecoratorSpec
    """The decorator specification that this property represents"""

    def shapes(self) -> tuple[Shape, ...]:
        return self.spec.shapes()


@dataclass
class ActiveLow(DecoratorSpec):
    """
    Active-low (bubble) pin decorator specification

    Creates a circle/bubble symbol to indicate active-low signals.
    """

    diameter: float = DEF_ACTIVE_LOW_DIAM
    """Diameter of the bubble in symbol grid units"""
    nudge: tuple[float, float] = DEF_ACTIVE_LOW_NUDGE
    """Offset to position the bubble aesthetically"""

    def shapes(self) -> tuple[Shape, ...]:
        return (
            Transform((-self.diameter / 2.0, 0))
            * Transform(self.nudge)
            * Circle(diameter=self.diameter),
        )

    def placement(self) -> DecoratorPlacement:
        return DecoratorPlacement.OUTSIDE


@dataclass
class OpenCollector(DecoratorSpec):
    """
    Open collector pin decorator specification

    Creates a diamond symbol with optional hat and pullup/pulldown indicator.
    """

    oc_type: OpenCollectorType = OpenCollectorType.SINK
    """Type of open collector (sink or source)"""
    width: float = DEF_OC_DEC_SIZE
    """Size of the diamond symbol"""
    line_width: float = DEF_LINE_WIDTH
    """Stroke width for the symbol lines"""
    pullup_down: bool = DEF_OC_PULL
    """Whether to show internal pullup/pulldown resistor indicator"""
    nudge: tuple[float, float] | None = None
    """Position offset for the symbol"""

    def __post_init__(self):
        if self.nudge is None:
            # Default nudge places the symbol inside the component body
            self.nudge = (self.width, 0.0)

    def shapes(self) -> tuple[Shape, ...]:
        w2 = self.width / 2.0
        shapes = []

        # Create diamond shape
        diamond_points = [
            (0.0, w2),
            (w2, 0.0),
            (0.0, -w2),
            (-w2, 0.0),
            (0.0, w2),  # Close the shape
        ]
        diamond = Polyline(self.line_width, diamond_points)
        shapes.append(diamond)

        # Add hat based on type
        hat_points = [(-w2, 0.0), (w2, 0.0)]
        if self.oc_type == OpenCollectorType.SOURCE:
            hat_y = w2
        else:  # SINK
            hat_y = -w2
        hat = Polyline(self.line_width, hat_points)
        hat_transform = Transform((0.0, hat_y))
        shapes.append(hat_transform * hat)

        # Add pullup/pulldown indicator if requested
        if self.pullup_down:
            pullup_line = Polyline(self.line_width, [(-w2, 0.0), (w2, 0.0)])
            shapes.append(pullup_line)

        # Apply nudge to all shapes
        assert self.nudge is not None  # __post_init__ ensures this is never None
        return tuple(Transform(self.nudge) * shape for shape in shapes)

    def placement(self) -> DecoratorPlacement:
        return DecoratorPlacement.INSIDE


@dataclass
class Clock(DecoratorSpec):
    """
    Clock pin decorator specification

    Creates a ">" shaped symbol to indicate clock inputs.
    """

    size: float | tuple[float, float] = DEF_CLOCK_SIZE
    """Size of the clock symbol"""
    line_width: float = DEF_LINE_WIDTH
    """Stroke width for the symbol lines"""

    def shapes(self) -> tuple[Shape, ...]:
        if isinstance(self.size, tuple):
            w, h = self.size
        else:
            w = h = self.size

        h2 = h / 2.0
        points = [(0.0, h2), (w / 2.0, 0.0), (0.0, -h2)]

        clock_shape = Polyline(self.line_width, points)
        return (clock_shape,)

    def placement(self) -> DecoratorPlacement:
        return DecoratorPlacement.INSIDE


@dataclass
class Cardinality(DecoratorSpec):
    """
    Pin cardinality specification

    This is a data structure that specifies the direction of signal flow for a pin
    (input, output, or bidirectional).
    """

    cardinality: CardinalityType
    """The direction of signal flow for this pin"""
    size: float | tuple[float, float] = DEF_CARD_SIZE
    """The size of the arrow symbols"""
    nudge: tuple[float, float] | None = None
    """The nudge offset for the arrow symbols"""

    def _default_nudge(self) -> tuple[float, float]:
        if isinstance(self.size, tuple):
            w = self.size[0]
        else:
            w = self.size
        # Default nudge places the arrow outside the symbol body (negative for outside)
        return (-w / 2.0, 0.0)

    def __post_init__(self):
        """Calculate default nudge if not provided"""
        if self.nudge is None:
            self.nudge = self._default_nudge()

    def shapes(self) -> tuple[Shape, ...]:
        if isinstance(self.size, tuple):
            w, h = self.size
            h2 = h / 2.0
        else:
            w = self.size
            h2 = w / 2.0

        shapes = []
        if self.cardinality == CardinalityType.INPUT:
            # Input arrow points inward (right)
            shapes.append(Polygon([(0.0, h2), (w / 2.0, 0.0), (0.0, -h2)]))
        elif self.cardinality == CardinalityType.OUTPUT:
            # Output arrow points outward (left)
            shapes.append(Polygon([(0.0, h2), (-w / 2.0, 0.0), (0.0, -h2)]))
        elif self.cardinality == CardinalityType.BIDIRECTIONAL:
            # Bidirectional has both arrows
            shapes.append(Polygon([(0.0, h2), (w / 2.0, 0.0), (0.0, -h2)]))
            shapes.append(Polygon([(0.0, h2), (-w / 2.0, 0.0), (0.0, -h2)]))

        assert self.nudge is not None  # __post_init__ ensures this is never None
        return tuple(Transform(self.nudge) * shape for shape in shapes)

    def placement(self) -> DecoratorPlacement:
        return DecoratorPlacement.OUTSIDE


def placement(spec: DecoratorSpec) -> DecoratorPlacement:
    """Get the placement type for a decorator spec"""
    return spec.placement()


def decorate(port: Port, spec: DecoratorSpec) -> None:
    """Decorate a port with a pin decorator spec"""
    PinDecorator(spec).assign(port)


def draw(
    decorator: DecoratorSpec, direction: Direction, at: Point
) -> tuple[Shape, ...]:
    if direction == Direction.Left:
        transform = Transform(at, 0, (1.0, 1.0))
    elif direction == Direction.Down:
        transform = Transform(at, 90, (1.0, 1.0))
    elif direction == Direction.Right:
        transform = Transform(at, 0, (-1.0, 1.0))
    elif direction == Direction.Up:
        transform = Transform(at, 90, (-1.0, 1.0))
    else:
        raise ValueError(f"Invalid direction: {direction}")
    return tuple(transform * shape for shape in decorator.shapes())


# Helpers for supplying decorator types
def Input(
    size: float | tuple[float, float] = DEF_CARD_SIZE,
    nudge: tuple[float, float] | None = None,
):
    return Cardinality(CardinalityType.INPUT, size, nudge)


def Output(
    size: float | tuple[float, float] = DEF_CARD_SIZE,
    nudge: tuple[float, float] | None = None,
):
    return Cardinality(CardinalityType.OUTPUT, size, nudge)


def Bidirectional(
    size: float | tuple[float, float] = DEF_CARD_SIZE,
    nudge: tuple[float, float] | None = None,
):
    return Cardinality(CardinalityType.BIDIRECTIONAL, size, nudge)


def OpenCollectorSource(
    width: float = DEF_OC_DEC_SIZE,
    line_width: float = DEF_LINE_WIDTH,
    pullup_down: bool = DEF_OC_PULL,
    nudge: tuple[float, float] | None = None,
):
    return OpenCollector(
        OpenCollectorType.SOURCE, width, line_width, pullup_down, nudge
    )


def OpenCollectorSink(
    width: float = DEF_OC_DEC_SIZE,
    line_width: float = DEF_LINE_WIDTH,
    pullup_down: bool = DEF_OC_PULL,
    nudge: tuple[float, float] | None = None,
):
    return OpenCollector(OpenCollectorType.SINK, width, line_width, pullup_down, nudge)
