from __future__ import annotations
from dataclasses import dataclass

from jitx import current
from jitx.net import Port
from jitx.si import (
    Constrain,
    ConstrainReferenceDifference,
    RoutingStructure,
    SignalConstraint,
    Topology,
)
from jitx.toleranced import Toleranced


class RMII(Port):
    txd = Port(), Port()
    "Transmit Data Bus"
    rxd = Port(), Port()
    "Receive Data Bus"

    ref_clk = Port()
    "Ref Clock (50MHz)"

    tx_en = Port()
    "Transmit Enable"
    crs_dv = Port()
    "Multiplexed Carrier Sense and Data Valid Line"

    rx_er: Port | None = None
    "Receive Error Line"

    def __init__(self, rx_er=False):
        if rx_er:
            self.rx_er = Port()

    @dataclass
    class Standard:
        bus_skew = Toleranced(0, 2e-9)
        """
        Allowed skew in seconds.

        RMII Databus Skew Specification

        This is a guideline specification. RMII v1.2 does not
        specify guidance because the 50MHz clock rate
        and TTL levels don't typically have issues meeting clock
        setup and hold times (See section 7.2).

        The default value provided by this function is 2nS
        which should be well within in the setup (4ns) and
        hold (2ns) expectation for a 20nS (50MHz) period.
        See section 7.4.
        """

        loss = 16.0
        """
        Max loss in dB.

        RMII Databus Max Loss Specification

        This a guideline specification. The RMII v1.2 does
        not specify any guidance for the max loss of the
        signals in the bus.
        """

        impedance = Toleranced.percent(50, 5)

    class Constraint(SignalConstraint["RMII"]):
        def __init__(
            self,
            standard: RMII.Standard | None = None,
            structure: RoutingStructure | None = None,
        ):
            std = standard or RMII.Standard()
            self.bus_skew = std.bus_skew
            self.loss = std.loss
            if structure is None:
                structure = current.substrate.routing_structure(std.impedance)
            self.structure = structure

        def constrain(self, src: RMII, dst: RMII):
            clk_topo = Topology(src.ref_clk, dst.ref_clk)

            bus_topos = (
                [Topology(s, d) for s, d in zip(src.txd, dst.txd, strict=True)]
                + [Topology(s, d) for s, d in zip(src.rxd, dst.rxd, strict=True)]
                + [
                    Topology(src.tx_en, dst.tx_en),
                    Topology(src.crs_dv, dst.crs_dv),
                ]
            )

            if src.rx_er and dst.rx_er:
                bus_topos.append(Topology(src.rx_er, dst.rx_er))

            self.add(
                ConstrainReferenceDifference(clk_topo, bus_topos).timing_difference(
                    self.bus_skew
                ),
                full_topo := Constrain(Topology(src, dst)).insertion_loss(self.loss),
            )

            if self.structure:
                full_topo.structure(self.structure)
