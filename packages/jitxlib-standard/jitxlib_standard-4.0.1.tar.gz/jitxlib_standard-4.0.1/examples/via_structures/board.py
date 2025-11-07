from jitx.substrate import Substrate
from jitx.layerindex import Side
from jitx.via import Via, ViaType
from jitx.si import PinModel
from jitx.sample import SampleStackup, SampleFabConstraints, SampleBoard

MultiLayerStackup = SampleStackup(6)
DefaultFabConstraints = SampleFabConstraints


class DefaultTHVia(Via):
    start_layer = 0
    stop_layer = 5
    diameter = 0.45
    hole_diameter = 0.3
    filled = False
    tented = Side.Top
    antipad_diameter = 0.1
    type = ViaType.MechanicalDrill


class DefaultMicroVia(Via):
    start_layer = 0
    stop_layer = 1
    diameter = 0.3
    hole_diameter = 0.1
    filled = True
    tented = Side.Top
    antipad_diameter = 0.1
    type = ViaType.LaserDrill

    models = {(0, 1): PinModel(0.01, 0.02)}


class DefaultSubstrate(Substrate):
    stackup = MultiLayerStackup
    constraints = DefaultFabConstraints()
    vias = [DefaultTHVia, DefaultMicroVia]


DefaultBoard = SampleBoard
