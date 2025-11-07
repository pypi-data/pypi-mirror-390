"""DisplayPort Protocol

DisplayPort is a serial protocol supporting high speed links for video+audio
`https://en.wikipedia.org/wiki/DisplayPort`

The functions and definitions in this file support defining DisplayPort
connections between sources and receivers on a printed circuit board.

## DisplayPort Blocking Capacitors

The DisplayPort specification calls for AC coupling for the data lanes. This is
typically achieved using a blocking capacitor.

The best way to achieve this is to use the
:py:meth:`~jitx.si.SignalConstraint.constrain_topology` mechanism.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from jitx import current
from jitx.common import Power
from jitx.container import inner
from jitx.net import DiffPair, Port
from jitx.si import (
    ConstrainReferenceDifference,
    DiffPairConstraint,
    DifferentialRoutingStructure,
    SignalConstraint,
    Topology,
)
from jitx.toleranced import Toleranced


class DisplayPort(Port):
    aux = DiffPair()
    "Auxiliary channel pair"
    lane = DiffPair(), DiffPair(), DiffPair(), DiffPair()
    "Four data transfer pairs"
    hpd = Port()
    "Hot-Plug Detect"

    @dataclass(frozen=True)
    class Standard:
        skew = Toleranced(0, 20e-12)
        "Allowed intra-pair skew"

        loss = 15.0
        "Allowed loss"

        pair_to_pair_skew: Toleranced
        "Allowed inter-pair skew"

        impedance = Toleranced.percent(100, 10)

    class Version(Standard, Enum):
        """Different DP versions and accompanying standard values. To tweak, use py:func:`dataclasses.replace`.

        >>> tweak_DP1p0 = dataclasses.replace(DisplayPort.Version.DP1p0, impedance=Toleranced.percent(100, 5))
        """

        DP1p0 = Toleranced(0, 2 * 400e-12)
        "10.80 Gbit/s / 4 lanes =>  2.7 Gbit/s / 10 UI =>  270 MHz clk"
        DP1p1 = Toleranced(0, 2 * 371e-12)
        "10.80 Gbit/s / 4 lanes =>  2.7 Gbit/s / 10 UI =>  270 MHz clk"
        DP1p2 = Toleranced(0, 2 * 337e-12)
        "21.60 Gbit/s / 4 lanes =>  5.4 Gbit/s / 10 UI =>  540 MHz clk"
        DP1p2a = Toleranced(0, 2 * 337e-12)
        "21.60 Gbit/s / 4 lanes =>  5.4 Gbit/s / 10 UI =>  540 MHz clk"
        DP1p3 = Toleranced(0, 2 * 231e-12)
        "32.40 Gbit/s / 4 lanes =>  8.1 Gbit/s / 10 UI =>  810 MHz clk"
        DP1p4 = Toleranced(0, 2 * 231e-12)
        "32.40 Gbit/s / 4 lanes =>  8.1 Gbit/s / 10 UI =>  810 MHz clk"
        DP1p4a = Toleranced(0, 2 * 231e-12)
        "32.40 Gbit/s / 4 lanes =>  8.1 Gbit/s / 10 UI =>  810 MHz clk"
        DP2p0 = Toleranced(0, 2 * 100e-12)
        "80.00 Gbit/s / 4 lanes => 20.0 Gbit/s / 10 UI => 2000 MHz clk"
        DP2p1 = Toleranced(0, 2 * 100e-12)
        "80.00 Gbit/s / 4 lanes => 20.0 Gbit/s / 10 UI => 2000 MHz clk"
        DP2p1a = Toleranced(0, 2 * 100e-12)
        "80.00 Gbit/s / 4 lanes => 20.0 Gbit/s / 10 UI => 2000 MHz clk"

    @inner
    class Constraint(SignalConstraint["DisplayPort"]):
        def __init__(
            self,
            standard: DisplayPort.Standard,
            structure: DifferentialRoutingStructure | None = None,
        ):
            if not structure:
                structure = current.substrate.differential_routing_structure(
                    standard.impedance
                )
            self.diffpair_constraint = DiffPairConstraint(
                skew=standard.skew, loss=standard.loss, structure=structure
            )
            self.inter_skew = standard.pair_to_pair_skew

        def constrain(self, src: DisplayPort, dst: DisplayPort):
            for s, d in zip(src.lane, dst.lane, strict=True):
                self.diffpair_constraint.constrain(s, d)
            self.diffpair_constraint.constrain(src.aux, dst.aux)
            self.add(
                ConstrainReferenceDifference(
                    Topology(src.lane[0].p, dst.lane[0].p),
                    [
                        Topology(s, d)
                        for s, d in zip(src.lane[1:], dst.lane[1:], strict=True)
                    ],
                ).timing_difference(self.inter_skew)
            )


class DisplayPortConnector(Port):
    dp = DisplayPort()
    "DisplayPort bundle for data communication"
    gnd = Port()
    """Ground connection

    There are five ground signals in the connector, but for simplicity we only
    have one in the bundle. Once on the board, there's no need for separated
    ground signals."""
    power = Power()
    config = Port(), Port()
    "Two configuration pins"
