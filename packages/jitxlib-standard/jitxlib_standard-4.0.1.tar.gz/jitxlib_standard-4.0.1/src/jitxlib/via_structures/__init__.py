import math
from typing import Sequence

from dataclasses import dataclass, field
from jitx.via import Via
from jitx.transform import Transform
from jitx.net import Net, Port, DiffPair, PortAttachment
from jitx.circuit import Circuit
from jitx.component import Component
from jitx.feature import KeepOut, Custom
from jitx.layerindex import LayerSet
from jitx.landpattern import Landpattern, Pad, PadMapping
from jitx.symbol import Symbol, Pin, SymbolMapping
from jitx.shapes import Shape
from jitx.shapes.primitive import Empty, Circle
from jitx._structural import Container


@dataclass
class ViaGroundCage:
    """Base class for defining the ground cage for a Via Structure"""

    via_def: type[Via]
    """ Via Definition for the ground cage vias. This definition will be used to
    instantiate each of the needed vias.
    """

    def place_via_cage(self, n: Net):
        """User is expected to override this method and generate the
        via instances needed for the cage.

        Args:
            n: Net to which the vias of the cage will be connected. This would
                typically be ground in most applications.
        """
        raise NotImplementedError("Missing 'place_via_cage' method for ViaGroundCage")


@dataclass
class PolarViaGroundCage(ViaGroundCage):
    """Polar Via Ground Cage
    This type implements a polar-coordinate system for defining the vias of the
    ground cage.
    """

    via_def: type[Via]
    """Via Definition to use for all of the via placements.
    """
    count: int
    """Total number of via placements. Must be positive.
    """
    radius: float
    """Radius in mm for the circular pattern of via placements. Must be positive.
    """
    theta: float = 0.0
    """Starting angle for the pattern. Value in degrees.
    Default value is 0.0 degrees which points to the right along the X axis.
    """
    skips: list[int] = field(default_factory=list)
    """ Skipped indices in the via pattern. Each value in this collection
    must be in the range `[0, count-1]`
    """

    pose: Transform = field(default_factory=Transform.identity)
    """ Change the location and placement of the ground cage
    with respect to the origin of the via structure. The
    default value is the `IDENTITY` transformation.
    """

    def __post_init__(self):
        assert self.count > 0
        assert self.radius > 0.0

        for i, skip in enumerate(self.skips):
            assert skip < self.count, (
                f"Skip[{i}]={skip} Not less than count '{self.count}'"
            )

    def place_via_cage(self, n: Net):
        def compute_loc(i: int) -> Transform:
            phase = 2.0 * math.pi * i / self.count
            phase += math.radians(self.theta)
            return Transform.rotate(math.degrees(phase)) * Transform.translate(
                self.radius, 0.0
            )

        valid_pos = [x for x in range(self.count) if x not in self.skips]

        via_set = []
        for i in valid_pos:
            tx = self.pose * compute_loc(i)
            v = self.via_def().at(tx)
            via_set.append(v)
            n += v

        # Debug Mode
        # if debug-mode:
        #   for i in 0 to count(v) do:
        #     val pos = pose * compute-pos(v, i)
        #     layer(debug-layer) = pos * Circle(0.1)


class AntiPad(Container):
    """Base class for Anti-Pad constructors"""

    def place_anti_pad(self):
        raise NotImplementedError("Missing 'place_anti_pad' method for Antipad")


@dataclass
class SimpleAntiPad(AntiPad):
    """Trivial Anti-Pad Generator
    This Anti-Pad type generates `KeepOut` shapes on the passed layers
    and then positions them according the the `pose` argument.
    """

    shape: Shape
    """ KeepOut shape to be applied to all requested layers.
    """
    layers: LayerSet
    """ Set of layers where keepout will be applied.
    """
    pose: Transform = field(default_factory=Transform.identity)
    """ Optional transform to apply to the antipads so that they can be
    positioned with respect to the via-structure's origin.
    This value is `Transform.identity` by default.
    """

    def place_anti_pad(self):
        self.KO = KeepOut(self.pose * self.shape, self.layers, pour=True)


class InsertionPoint(Container):
    """Base class for insertion point in the layout.
    NOTE: The current tool doesn't support placing actual insertion
    points from code. Eventually we would like to support this.
    """

    def place_insertion_point(self):
        raise NotImplementedError(
            "Missing 'place_insertion_point' method for Insertion Point Decoration"
        )


@dataclass
class InsertionPointDecorator(InsertionPoint):
    """Construct a custom layer decoration that indicates where an
    insertion point should be place manually by the user. Typically,
    the user would drag out from the via so that it will follow as the
    via structure moves.
    """

    scale: float = 1.0
    layerName: str = "insertpt"
    pose: Transform = field(default_factory=Transform.identity)

    def __post_init__(self):
        assert self.scale > 0.0
        assert len(self.layerName) > 0

    def place_insertion_point(self):
        # sh = bullseye([0.15, 0.25], 0.1)
        sh = Circle(radius=0.15)
        self.insertPt = Custom(self.pose * sh, name=self.layerName)


class TopoSymbol(Symbol):
    """Dummy Symbol for the via structure `TopoPin` component."""

    p = Pin(at=(0, 0), length=3)

    def __init__(self):
        self.body = Circle(diameter=1.0)


class TopoPad(Pad):
    """Dummy Pad for the `TopoLP`.
    This pad is an empty shape and only serves to be
    a location for identifying the `TopoPin`'s port
    in the physical design.
    """

    def __init__(self):
        self.shape = Empty()


class TopoLP(Landpattern):
    """Dummy Landpattern for the `TopoPin` construct
    for creating via structures.
    """

    def __init__(self):
        self.p = TopoPad().at(0.0, 0.0)


class TopoPin(Component):
    """Define a component for holding the via structrure's pin definition.
    For a single-ended via, one of these instances is created.
    For a diff-pair via, two are created.
    """

    p = Port()

    def __init__(self):
        self.symb = TopoSymbol()
        self.lp = TopoLP()
        self.cmappings = [
            SymbolMapping({self.p: self.symb.p}),
            PadMapping({self.p: self.lp.p}),
        ]


class ViaStructure(Circuit):
    """Base class for ViaStructure definitions"""

    def __init__(
        self,
        ground_cages: Sequence[ViaGroundCage],
        antipads: Sequence[AntiPad],
        insertion_points: Sequence[InsertionPoint],
    ):
        """Constructor for base class

        Args:
            ground_cages - Set of zero or more ground cage structures.
            antipads - Set of zero or more antipad definitions to apply to the via structure.
            insertion_points - Set of zero or more insertion point locators.
        """

        # via structures are floating, they vias are in a fixed position inside
        self.at(floating=True)
        self.ground_cages = ground_cages
        self.antipads = antipads
        self.insertion_points = insertion_points

    def generate_common_structures(self, common: Net):
        for gndCage in self.ground_cages:
            gndCage.place_via_cage(common)

        for antipad in self.antipads:
            antipad.place_anti_pad()

        for insert in self.insertion_points:
            insert.place_insertion_point()

    @staticmethod
    def create_std_insertion_points(radius: float):
        assert radius > 0.0
        offset = Transform.translate(0, radius)
        return [
            InsertionPointDecorator(pose=offset),
            InsertionPointDecorator(pose=Transform.rotate(180.0) * offset),
        ]


class SingleViaStructure(ViaStructure):
    """Single-Ended Signal Via structure
    This object constructs a Circuit definition that can generate
    via structure instances for single-ended signals (ie single `Port` nets).
    User must instantiate an via structure instance and net/topo it in the
    circuit like a normal component.
    """

    sig_in = Port()
    sig_out = Port()
    COMMON = Port()

    def __init__(
        self,
        via_def: type[Via],
        *,
        ground_cages: Sequence[ViaGroundCage],
        antipads: Sequence[AntiPad],
        insertion_points: Sequence[InsertionPoint],
    ):
        """Construct a single-ended via structure instance

        Args:
            via_def: Via Type that will be instantiated to construct
                the signal via for the structure.
            ground_cages - Set of zero or more ground cage structures.
            antipads - Set of zero or more antipad definitions to apply to the via structure.
            insertion_points - Set of zero or more insertion point locators.
        """
        super().__init__(ground_cages, antipads, insertion_points)

        self.GND = Net(name="COMMON_n")
        self.GND += self.COMMON

        self.sigComp = TopoPin().at(0.0, 0.0)

        self.TOPO = self.sig_in >> self.sigComp.p >> self.sig_out

        self.attached = PortAttachment(self.sigComp.p, via_def().at(0.0, 0.0))

        self.generate_common_structures(self.GND)


class DifferentialViaStructure(ViaStructure):
    """Differential Pair Via Structure
    This object constructs a Circuit definition that can generate a
    via structure instance for support a `DiffPair` port net.
    User must instantiate an instance of this via structure type and
    net/topo it into the circuit like a normal component instance.
    """

    sig_in = DiffPair()
    sig_out = DiffPair()
    COMMON = Port()

    def __init__(
        self,
        via_defs: type[Via] | tuple[type[Via], type[Via]],
        pitch: float,
        *,
        ground_cages: Sequence[ViaGroundCage],
        antipads: Sequence[AntiPad],
        insertion_points: Sequence[InsertionPoint],
    ):
        """Construct a new Differential Via Structure instance.

        Args:
            via_defs: Via Type that will be instantiated to construct
                the signal vias for the structure. If this value is a tuple
                of 2 Via definitions, then we will use separate via definitions
                for the P and N signals, respectively.
            pitch: Distance between the P and N signal vias in mm.
            ground_cages - Set of zero or more ground cage structures.
            antipads - Set of zero or more antipad definitions to apply to the via structure.
            insertion_points - Set of zero or more insertion point locators.
        """
        super().__init__(ground_cages, antipads, insertion_points)

        if not isinstance(via_defs, tuple):
            via_defs = (via_defs, via_defs)

        assert len(via_defs) == 2
        assert pitch > 0

        self.GND = Net(name="COMMON_n")
        self.GND += self.COMMON

        self.P_comp = TopoPin().at(pitch / 2, 0.0)
        self.N_comp = TopoPin().at(-pitch / 2, 0.0)

        self.TOPO_P = self.sig_in.p >> self.P_comp.p >> self.sig_out.p
        self.TOPO_N = self.sig_in.n >> self.N_comp.p >> self.sig_out.n

        self.ATTACH_P = PortAttachment(self.P_comp.p, via_defs[0]().at(pitch / 2, 0.0))
        self.ATTACH_N = PortAttachment(self.N_comp.p, via_defs[1]().at(-pitch / 2, 0.0))

        self.generate_common_structures(self.GND)
