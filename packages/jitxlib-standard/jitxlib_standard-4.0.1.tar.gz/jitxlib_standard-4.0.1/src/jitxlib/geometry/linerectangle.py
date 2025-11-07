from jitx.anchor import Anchor
from jitx.shapes import Shape
from jitx.shapes.primitive import Polyline
from jitx.transform import IDENTITY, Transform


def line_rectangle(
    width: float,
    height: float,
    line_width: float,
    transform: Transform = IDENTITY,
    anchor: Anchor = Anchor.C,
) -> Shape[Polyline]:
    """
    Create a polyline that represents a rectangle with lines.
    """
    vt, hr = anchor.vertical(), anchor.horizontal()
    match hr:
        case Anchor.W:
            xc = width / 2
        case Anchor.C:
            xc = 0
        case Anchor.E:
            xc = -width / 2

    match vt:
        case Anchor.S:
            yc = height / 2
        case Anchor.C:
            yc = 0
        case Anchor.N:
            yc = -height / 2

    w2, h2 = width / 2, height / 2
    line = Polyline(
        line_width,
        [
            (xc - w2, yc - h2),
            (xc + w2, yc - h2),
            (xc + w2, yc + h2),
            (xc - w2, yc + h2),
            (xc - w2, yc - h2),  # Close the rectangle
        ],
    )
    return transform * line
