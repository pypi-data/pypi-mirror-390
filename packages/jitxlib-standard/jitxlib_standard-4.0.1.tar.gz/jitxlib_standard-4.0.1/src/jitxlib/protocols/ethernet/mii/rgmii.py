from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from jitx import current
from jitx.container import inner
from jitx.net import Port
from jitx.si import (
    ConstrainReferenceDifference,
    RoutingStructure,
    SignalConstraint,
    Constrain,
    Topology,
)
from jitx.toleranced import Toleranced


class RGMII(Port):
    """Reduced Gigabit Media Independent Interface (RGMII)
    see `https://en.wikipedia.org/wiki/Media-independent_interface#RGMII`

    This bundle is structured as a py:class:`jitx.common.LanePair` bundle.
    """

    class Lane(Port):
        """RGMII Lane Bundle"""

        data = Port(), Port(), Port(), Port()
        "Data bus"

        clk = Port()
        "Clock line"

        ctl = Port()
        "Multiplexed enable and error signals"

    TX = Lane()
    "Transmit Lane"
    RX = Lane()
    "Receive Lane"

    @dataclass
    class Standard:
        data_to_clock_delay: Toleranced
        "This is the expected delay between data to clock."

        loss = 7.5
        "This is the max loss in dB for all signals."

        bus_skew = Toleranced(0, 11e-12)
        "Databus skew specification."

        impedance = Toleranced.percent(50, 15)
        "Impedance spec for single-ended traces."

        @inner
        class Constraint(SignalConstraint["RGMII"]):
            def __init__(
                self,
                standard: RGMII.Standard,
                structure: RoutingStructure | None = None,
            ):
                self.loss = standard.loss
                self.bus_skew = standard.bus_skew
                self.data_to_clock_delay = standard.data_to_clock_delay
                if structure is None:
                    structure = current.substrate.routing_structure(standard.impedance)
                self.structure = structure

            def constrain(self, src: RGMII, dst: RGMII):
                for sln, dln in zip((src.TX, src.RX), (dst.TX, dst.RX), strict=True):
                    clk_top = Topology(sln.clk, dln.clk)
                    bus_tops = [
                        Topology(s, d) for s, d in zip(sln.data, dln.data, strict=True)
                    ]
                    ctl_top = Topology(sln.ctl, dln.ctl)
                    self.add(
                        all_tops := Constrain(
                            [clk_top] + bus_tops + [ctl_top]
                        ).insertion_loss(self.loss),
                        ConstrainReferenceDifference(
                            ctl_top, bus_tops
                        ).timing_difference(self.bus_skew),
                        ConstrainReferenceDifference(
                            clk_top, ctl_top
                        ).timing_difference(self.data_to_clock_delay),
                    )

                    if self.structure:
                        all_tops.structure(self.structure)

    class Version(Standard, Enum):
        """RGMII Version

        RGMII v1 requires a specific Data to Clock delay in the PCB board to
        meet setup and hold times.

        In RGMII v2, the spec introduces an optional "Internal Delay"
        feature. Devices that provide this are labeled "RGMII-ID".
        These devices don't require a PCB board delay because the
        delay can be configured in firmware.
        """

        # min-max(1.0e-9, 2.6e-9)
        STD = Toleranced.min_max(1.5e-9, 2e-9)
        ID = Toleranced(0, 0.5e-9)
