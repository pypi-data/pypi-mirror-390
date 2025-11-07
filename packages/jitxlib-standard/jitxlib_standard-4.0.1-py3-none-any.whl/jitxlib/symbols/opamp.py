from jitx.anchor import Anchor
from jitx.shapes.primitive import Polyline, Text
from jitx.symbol import Direction, Pin, Symbol


class OpAmpSymbol(Symbol):
    pin_name_size = 0.7
    pad_name_size = 0.7
    OUT = Pin((4, 0), 4, Direction.Right)
    Vp = Pin((0, 4), 4, Direction.Up)
    INn = Pin((-4, 2), 4, Direction.Left)
    INp = Pin((-4, -2), 4, Direction.Left)
    Vn = Pin((0, -4), 4, Direction.Down)

    value = Text(">VALUE", 0.5, Anchor.C).at(0, 5)
    reference = Text(">REF", 0.5, Anchor.C).at(0, 5.7)
    art = [
        # Op-amp triangle
        Polyline(0.2, [(-4, -4), (4, 0), (-4, 4), (-4, -4)]),
        # Power supply lines
        Polyline(0.2, [(0, -2), (0, -4)]),
        Polyline(0.2, [(0, 4), (0, 2)]),
        # Input symbols
        Polyline(0.2, [(-3.2, -2), (-2, -2)]),  # + symbol horizontal
        Polyline(0.2, [(-2.6, -1.4), (-2.6, -2.6)]),  # + symbol vertical
        Polyline(0.2, [(-3.2, 2), (-2, 2)]),  # - symbol
    ]
