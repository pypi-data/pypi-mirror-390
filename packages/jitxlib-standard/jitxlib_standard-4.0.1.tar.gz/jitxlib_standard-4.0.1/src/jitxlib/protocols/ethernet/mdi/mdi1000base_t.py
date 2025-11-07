"""MDI - Media Dependent Interface

This module defines the MDI bundle and associated constraint functions
for the 1000Base-T Ethernet standard.

Create a 1000Base-T MDI Constraint and apply it to a simple topology
>>> class EthernetCircuit(Circuit):
...     def __init__(self):
...         self.ethernet_jack = EthernetJack(), EthernetJack()
...         eth0 = ethernet_jack[0].require(MDI1000BaseT)
...         eth1 = ethernet_jack[1].require(MDI1000BaseT)
...         self.mdiconstraint = MDI1000BaseT.Constraint()
...         with self.mdiconstraint.constrain_topology(eth0, eth1) as (src, dst):
...             self += src >> dst

Create a 1000Base-T MDI Constraint and apply it to a complex topology
>>> class EthernetCircuit(Circuit):
...     def __init__(self):
...         self.ethernet_jack = EthernetJack(), EthernetJack()
...         eth0 = ethernet_jack[0].require(MDI1000BaseT)
...         eth1 = ethernet_jack[1].require(MDI1000BaseT)
...         self.mdiconstraint = MDI1000BaseT.Constraint()
...         self.esd_pool = ESDPool(2)
...         with self.mdiconstraint.constrain_topology(eth0, eth1) as (src, dst):
...             for p in range(4):
...                 protected = self.esd_pool.require(DualPair)
...                 self += src.TP[p] >> protected.A >> protected.B >> dst.TP[p]
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

from jitx.container import Container
from jitx.net import DiffPair, Port, Provide
from jitx.si import (
    ConstrainReferenceDifference,
    DiffPairConstraint,
    DifferentialRoutingStructure,
    SignalConstraint,
    Topology,
)
from jitx.toleranced import Toleranced
from jitx import current


class MDI1000BaseT(Port):
    TP = DiffPair(), DiffPair(), DiffPair(), DiffPair()

    @dataclass
    class Standard:
        skew = Toleranced(0, 1.6e-12 / 2)
        "Intra pair skew - Allowable delay difference as a `Toleranced` value in Seconds."

        loss = 12
        "Max allowable power loss limit in dB."

        impedance = Toleranced.percent(95, 15)
        "The expected differential impedance for the differential pairs in Ohms"

        pair_to_pair_skew = Toleranced(0, 330e-12 / 2)
        "Allowable inter-pair delay difference as a `Toleranced` value in Seconds."

    class Constraint(SignalConstraint["MDI1000BaseT"]):
        diffpair_constraint: DiffPairConstraint
        inter_skew: Toleranced

        def __init__(
            self,
            standard: MDI1000BaseT.Standard | None = None,
            structure: DifferentialRoutingStructure | None = None,
        ):
            std = standard or MDI1000BaseT.Standard()
            if not structure:
                structure = current.substrate.differential_routing_structure(
                    std.impedance
                )
            self.diffpair_constraint = DiffPairConstraint(
                skew=std.skew, loss=std.loss, structure=structure
            )
            self.inter_skew = std.pair_to_pair_skew

        def constrain(self, src: MDI1000BaseT, dst: MDI1000BaseT):
            super().constrain(src, dst)

            for s, d in zip(src.TP, dst.TP, strict=True):
                self.diffpair_constraint.constrain(s, d)

            self.add(
                ConstrainReferenceDifference(
                    Topology(src.TP[0].p, dst.TP[0].p),
                    (Topology(s, d) for s, d in zip(src.TP, dst.TP, strict=True)),
                ).timing_difference(self.inter_skew)
            )

    class Provide(Container):
        """Construct provider for a 1000Base-T connection.

        This constructs a provider for a 1000Base-T (Gigabit) MDI interface.
        This includes creating the appropriate option mappings for swapping the
        differential pairs.

        >>> self += MDI1000BaseT.Provide(
        ...     [self.C.TXRX1A, self.C.TXRX1B, self.C.TXRX1C, self.C.TXRX1D]
        ... )
        """

        def __init__(self, diffpairs: Sequence[DiffPair] | Sequence[tuple[Port, Port]]):
            """Constructor for the MDI 1000Base-T Pin Assignment Provider.
            This provider constructs the diff-pair assignments for 1000Base-T
            connection including the valid swaps for the A/B and C/D pairs.

            Args:
                diffpairs: User can provide the diff-pair ports for the provider
                    one of two forms:
                    1. A sequence of `DiffPair` ports, one for each of the four pairs.
                    2. A sequence of tuples where each tuple contains the positive and negative
                        signal port for each differential pair. The order of each pair is `(P, N)`.
            """
            assert len(diffpairs) == 4
            self.options = Provide(MDI1000BaseT)

            @self.options.one_of
            def bundle_swaps(bundle: MDI1000BaseT):
                pair_maps = (
                    (0, 1, 2, 3),  # Straight Through
                    (1, 0, 2, 3),  # A/B swapped
                    (0, 1, 3, 2),  # C/D swapped
                    (1, 0, 3, 2),  # A/B & C/D swapped
                )
                straight = (0, 1, 2, 3)

                def get_P(pair: DiffPair | tuple[Port, Port]) -> Port:
                    if isinstance(pair, DiffPair):
                        return pair.p
                    else:
                        return pair[0]

                def get_N(pair: DiffPair | tuple[Port, Port]) -> Port:
                    if isinstance(pair, DiffPair):
                        return pair.n
                    else:
                        return pair[1]

                mapP = [
                    [
                        (bundle.TP[a].p, get_P(diffpairs[b]))
                        for a, b in zip(swapped, straight, strict=True)
                    ]
                    for swapped in pair_maps
                ]
                mapN = [
                    [
                        (bundle.TP[a].n, get_N(diffpairs[b]))
                        for a, b in zip(swapped, straight, strict=True)
                    ]
                    for swapped in pair_maps
                ]
                return [a + b for a, b in zip(mapP, mapN, strict=True)]
