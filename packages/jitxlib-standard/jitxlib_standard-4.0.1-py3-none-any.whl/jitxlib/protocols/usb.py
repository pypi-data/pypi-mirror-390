"""
USB Protocol
============

This package contains the definitions for the Universal Serial Bus protocol.

`https://en.wikipedia.org/wiki/USB`_
`https://www.usb.org/`_


Transport vs Connector Bundles
------------------------------


The USB protocol contains many different layers from physical to logical. The bundles in
this package are organized to support two levels in the application:

  1. Transport - This is the set of signals that convey the information in the
     bus. These signals typically traverse many components from the connector to
     the processor endpoint.

     These signals typically have SI constraints attached to them.

  2. Connector - This is the physical layer where the USB cable meets the
     board. This interface may have power, shield, and other accessory pins in
     addition to the transport layer signals. These additional connections may
     or may not make there way to the processor endpoint.

In the code below, the "transport" bundles are what you would typically use
when connecting up the different modules of your circuit. The "connector"
bundles are typically used to define the ports on a physical connector
component or module that contains the physical connector component.


Symmetry in Transport Bundles
-----------------------------

If you look closely at the bundles defined below, you will notice some symmetry
in the definitions of the transport bundles.

The :py:class:`USBData` bundle defines the USB2.0 interface with port ``data``.
This same interface gets reused in :py:class:`USBSuperSpeed` and
:py:class:`USB_C` later on.

Similarly, we use ``lane`` to define an array of
:py:class:`~jitx.common.LanePair`` bundles (RX + TX differential pairs). This
same pattern gets used in :py:class:`USB_C`.

This is not by accident. The reason we structure the bundles this way is:

  1. They can easily used in ``provide/require`` pin assignment statements.
  2. We can simplify the implementation of the connect, constrain, and routing
     structure application functions.

Matching Lanes
--------------

For most of the constraint functions in this package, the bundle types
themselves are not checked for equality. Instead - we check for matching
lane configurations. This allows a :py:class:`USBSuperSpeed` and
:py:class:`USB_C` transport bundle to connect to each other if they have the
correct number of lanes defined.
"""

from __future__ import annotations
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from jitx import current
from jitx.common import LanePair, Power
from jitx.inspect import extract
from jitx.net import DiffPair, Port
from jitx.si import DiffPairConstraint, DifferentialRoutingStructure, SignalConstraint
from jitx.toleranced import Toleranced
from jitx.container import inner


class USB2(Port):
    """
    Transport Bundle for the USB 2.0 Interface
    """

    data = DiffPair()
    "Differential pair for USB data"


class USB2Connector(Port):
    """
    Connector Bundle for the USB 2.0 Interface
    """

    vbus = Power()
    ":py:class:`Power` bundle for USB connector interface"
    bus = USB2()
    ":py:class:`USB2` bundle (differential pair)"
    id = Port()
    "ID signal"


class USBSuperSpeed(USB2):
    """
    Transport Bundle for Superspeed USB

    This bundle supports USB 3/4 transport signals. These are the signals
    that are typically connected with SI constraints from the connector
    to the MCU or other components.

    This bundle type is usually used to construct the ports on MCUs,
    ESD devices, Muxes, etc in the USB 3/4 applications.

    Args:
        lane_count: Number of superspeed lanes in this bundle.
    """

    lane: Sequence[LanePair]
    "A configurable number of lane-pairs for data transfer"

    def __init__(self, lane_count=2):
        self.lane = tuple(LanePair() for _ in range(lane_count))


class USBSuperSpeedConnector(Port):
    """
    Connector Bundle for USB Type A SuperSpeed™ Connectors
    """

    vbus = Power()
    ":py:class:`Power` bundle for USB connector interface"
    bus = USBSuperSpeed()
    ":py:class:`USBSuperSpeed` bundle for high speed data transfer"
    shield = Port()
    "Pin for connection to cable shield"


class USB_C(USBSuperSpeed):
    """
    Transport Bundle for USB3/4

    Args:
        lane_count: Number of superspeed lanes in this bundle.
    """

    cc = Port(), Port()
    "CC pins for capability identification"
    sbu = Port(), Port()
    "SBU pins for side band utility"

    def __init__(self, lane_count=2):
        super().__init__(lane_count)


class USB_C_Connector(Port):
    """
    Connector Bundle - USB Type C Connector

    This bundle is typically applied to a physical connector
    component in a board design.
    """

    vbus = Power()
    ":py:class:`Power` bundle for USB connector interface"
    bus = USB_C()
    ":py:class:`USB_C` bundle for high speed data transfer"
    shield = Port()
    "Pin for connection to cable shield"


#########################
# Constraints
#########################


@dataclass(frozen=True)
class USBStandard:
    skew: Toleranced
    impedance: Toleranced
    loss = 12.0

    @inner
    class Constraint[T: USB2](SignalConstraint[T]):
        """Construct a :py:class:`SignalConstraint` applicable to USB topologies of this standard."""

        def __init__(
            self,
            std: USBStandard,
            structure: DifferentialRoutingStructure | None = None,
        ):
            if structure is None:
                structure = current.substrate.differential_routing_structure(
                    std.impedance
                )
            self.diffpair_constraint = DiffPairConstraint(std.skew, std.loss, structure)

        def constrain(self, src: USB2, dst: USB2):
            for sdp, ddp in zip(
                extract(src, DiffPair), extract(dst, DiffPair), strict=True
            ):
                self.diffpair_constraint.constrain(sdp, ddp)


class USB(USBStandard, Enum):
    v2 = Toleranced(0, 3.75e-12), Toleranced.percent(90, 15)
    v3 = Toleranced(0, 1e-12), Toleranced.percent(90, 15)
    v4 = Toleranced(0, 1e-12), Toleranced(85, 9)
