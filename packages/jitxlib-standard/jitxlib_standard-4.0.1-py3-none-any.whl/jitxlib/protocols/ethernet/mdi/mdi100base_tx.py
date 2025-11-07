from __future__ import annotations

from jitx import current
from jitx.common import LanePair
from jitx.si import (
    DiffPairConstraint,
    DifferentialRoutingStructure,
    SignalConstraint,
    dataclass,
)
from jitx.toleranced import Toleranced


class MDI100BaseTX(LanePair):
    @dataclass
    class Standard:
        skew = Toleranced(0, 750e-12)
        "Intra pair skew - Allowable delay difference as a `Toleranced` value in Seconds."

        loss = 12
        "Max allowable power loss limit in dB."

        impedance = Toleranced.percent(100, 10)
        "The expected differential impedance for the differential pairs in Ohms"

    class Constraint(SignalConstraint["MDI100BaseTX"]):
        diffpair_constraint: DiffPairConstraint

        def __init__(
            self,
            standard: MDI100BaseTX.Standard,
            structure: DifferentialRoutingStructure | None = None,
        ):
            if structure is None:
                structure = current.substrate.differential_routing_structure(
                    standard.impedance
                )
            self.diffpair_constraint = DiffPairConstraint(
                skew=standard.skew, loss=standard.loss, structure=structure
            )

        def constrain(self, src: MDI100BaseTX, dst: MDI100BaseTX):
            self.diffpair_constraint.constrain(src.TX, dst.TX)
            self.diffpair_constraint.constrain(src.RX, dst.RX)
