import jitx
import jitx.test
from jitx.shapes import Shape
from jitx.shapes.primitive import Circle, Empty
from jitx.shapes.composites import rectangle
from jitx.feature import Soldermask, Paste, Cutout, Feature

from jitxlib.landpatterns.pads import SMDPad, THPad


def get_shape(feature: Feature | None) -> Shape:
    if feature is None:
        return Empty()
    return feature.shape


class SMDPadTestCase(jitx.test.TestCase):
    def test_basic(self):
        uut = SMDPad(Circle(diameter=1.0), soldermask=0.1, paste=-0.1)
        assert isinstance(uut.shape, Shape)

        self.assertIsInstance(uut.soldermask, Soldermask)
        self.assertIsInstance(uut.paste, Paste)

        Cu = uut.shape.to_shapely()
        Sm = get_shape(uut.soldermask).to_shapely()
        Pa = get_shape(uut.paste).to_shapely()

        self.assertTrue(Cu.contains(Pa))
        self.assertTrue(Sm.contains(Cu))

        uut = SMDPad(Circle(diameter=1.0), soldermask=0.1, paste=rectangle(0.5, 0.5))
        assert isinstance(uut.shape, Shape)
        self.assertIsInstance(uut, SMDPad)

        self.assertIsInstance(uut.soldermask, Soldermask)
        self.assertIsInstance(uut.paste, Paste)

        Cu = uut.shape.to_shapely()
        Sm = get_shape(uut.soldermask).to_shapely()
        Pa = get_shape(uut.paste).to_shapely()

        self.assertTrue(Cu.contains(Pa))
        self.assertTrue(Sm.contains(Cu))


class ThroughHolePadTestCase(jitx.test.TestCase):
    def test_basic(self):
        uut = THPad(Circle(diameter=1.0), cutout=Circle(diameter=0.1), soldermask=0.2)

        assert isinstance(uut.shape, Shape)
        self.assertIsInstance(uut.cutout, Cutout)
        self.assertIsInstance(uut.soldermask, Soldermask)
        # self.assertFalse(hasattr(uut, "paste"))

        Ho = get_shape(uut.cutout).to_shapely()
        Cu = uut.shape.to_shapely()
        Sm = get_shape(uut.soldermask).to_shapely()

        self.assertTrue(Cu.contains(Ho))
        self.assertTrue(Sm.contains(Cu))
        self.assertTrue(Sm.contains(Ho))

        uut = THPad(
            Circle(diameter=1.0),
            cutout=Circle(diameter=0.1),
            soldermask=0.2,
            paste=-0.1,
        )
        assert isinstance(uut.shape, Shape)

        self.assertIsInstance(uut.cutout, Cutout)
        self.assertIsInstance(uut.soldermask, Soldermask)
        self.assertIsInstance(uut.paste, Paste)

        Ho = get_shape(uut.cutout).to_shapely()
        Cu = uut.shape.to_shapely()
        Sm = get_shape(uut.soldermask).to_shapely()
        Pa = get_shape(uut.paste).to_shapely()

        self.assertTrue(Cu.contains(Ho))
        self.assertTrue(Sm.contains(Cu))
        self.assertTrue(Sm.contains(Ho))
        self.assertTrue(Cu.contains(Pa))

    def test_invalid_copper(self):
        with self.assertRaises(ValueError):
            THPad(Circle(diameter=1.0), cutout=Circle(diameter=-0.1), soldermask=0.2)

        with self.assertRaises(ValueError):
            THPad(Circle(diameter=0.5), cutout=Circle(diameter=1.0), soldermask=0.2)
