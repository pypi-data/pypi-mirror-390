from jitx.circuit import Circuit
from jitx.component import Component
from jitx.net import Port
from jitx.sample import SampleDesign

from jitxlib.landpatterns.ipc import DensityLevel, DensityLevelContext
from jitxlib.landpatterns.twopin.smt import PolarizedSMT, SMT
from jitxlib.symbols.box import BoxSymbol


class SMTComponent(Component):
    def __init__(
        self,
        case_name: str,
        polarized: bool = False,
        density_level: DensityLevel | None = None,
    ):
        if polarized:
            self.a = Port()
            self.c = Port()
        else:
            self.ports = [Port(), Port()]
        self.symbol = BoxSymbol()

        if polarized:
            self.landpattern = PolarizedSMT(case_name)
        else:
            self.landpattern = SMT(case_name)
        if density_level is not None:
            self.landpattern.density_level(density_level)


class MainCircuit(Circuit):
    c1 = SMTComponent("1206")
    c2 = SMTComponent("1206", polarized=True)
    c3 = SMTComponent("0402")
    c4 = SMTComponent("0402", polarized=True)
    c5 = SMTComponent("0603")
    c6 = SMTComponent("0603", polarized=True)
    c7 = SMTComponent("0805")
    c8 = SMTComponent("0805", polarized=True)
    c9 = SMTComponent("1210", polarized=True, density_level=DensityLevel.B)


class SMTTestDesign(SampleDesign):
    density_level = DensityLevelContext(DensityLevel.A)
    circuit = MainCircuit()
