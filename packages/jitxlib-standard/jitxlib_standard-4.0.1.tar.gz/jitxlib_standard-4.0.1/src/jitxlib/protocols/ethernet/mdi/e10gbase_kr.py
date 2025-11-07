"""
10GBASE-KR Protocol

10GBASE-KR is a ethernet communication supporting high speed data links
in copper for backplane connections.
See `10 Gigabit Ethernet <https://en.wikipedia.org/wiki/10_Gigabit_Ethernet#10GBASE-KR>`

This functions and definitions in this file support defining 10GBASE-KR
connections between components and/or connectors in a board design.

## 10GBASE-KR Blocking Capacitors

The 10GBASE-KR specification calls for AC coupling for the data lanes. This is
typically achieved using a blocking capacitor. When connecting two active
components, this typically means blocking caps from ``Tx -> Rx`` on both sides
of the link. When connecting an active component to a passive component, this
typically means adding the blocking caps only on the ``Tx -> Rx`` side of the
link.

The functions in this module allow you to pass a blocking capacitor as an
instantiable.  This component will get instantiated for each leg of the
diff-pair. These functions handle the topology configuration, but the user
needs to set a :py:class:`jitx.si.BridgingPinModel` on the capacitor component.
"""

from __future__ import annotations
from dataclasses import dataclass

from jitx import current
from jitx.net import DiffPair, Port
from jitx.si import DiffPairConstraint, DifferentialRoutingStructure, SignalConstraint
from jitx.toleranced import Toleranced


class LanePair(Port):
    TX = DiffPair()
    RX = DiffPair()


class E10GBaseKR(Port):
    def __init__(self, lanes: int):
        self.lane = [LanePair() for _ in range(lanes)]

    @dataclass
    class Standard:
        """Curated values for skew and loss of 10GBASE-KR Channel

        This is a helper class that returns the bounds on the intra-pair
        skew timing and maximum loss as expected by the particular standard targeted by
        the user.The values returned are a toleranced value with upper/lower limits for the
        intra-pair skew and the maximum loss as a double representing dB. Some defaults in the
        table are derived from the reference listed below.
        `https://www.ieee802.org/3/ba/public/jul08/balasubramanian_01_0708.pdf`

        Calculating the intra-pair skew distance to time correspondence depends on the material.
        see `http://pdf.cloud.opensystemsmedia.com/advancedtca-systems.com/Simclar.Feb08.pdf`
        Table 3 where the intra-pair skew is set to 0.0625e-12 and the inter-pair skew
        is set to 0.625e-12. This corresponds roughly to 0.01mm skew intra-pair and
        0.100mm skew inter-pair (or lane).
        """

        skew = Toleranced(0, 0.0625e-12)
        "Allowed intra-pair skew in seconds"
        pair_to_pair_skew = Toleranced(0, 0.0625e-12)
        "Allowed inter-pair skew in seconds"
        loss = 15.0
        "Maximum loss in dB"
        impedance = Toleranced.percent(100, 10)
        "Differential impedance specified by the e10GBASE-KR standard"

    class Constraint(SignalConstraint["E10GBaseKR"]):
        def __init__(
            self,
            standard: E10GBaseKR.Standard | None = None,
            structure: DifferentialRoutingStructure | None = None,
        ):
            std = standard or E10GBaseKR.Standard()
            if structure is None:
                structure = current.substrate.differential_routing_structure(
                    std.impedance
                )
            self.diffpair_constraint = DiffPairConstraint(
                std.skew, std.loss, structure=structure
            )

        def constrain(self, src: E10GBaseKR, dst: E10GBaseKR):
            for s, d in zip(src.lane, dst.lane, strict=True):
                self.diffpair_constraint.constrain(s.TX, d.TX)
                self.diffpair_constraint.constrain(s.RX, d.RX)
            # TODO this seems incomplete
