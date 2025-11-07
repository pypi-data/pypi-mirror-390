"""
A collection of serial communication protocols
"""

from collections.abc import Sequence
from jitx.net import Port


class I2C(Port):
    """Inter-Integrated Circuit (I2C) - Serial Communication Protocol

    see `https://en.wikipedia.org/wiki/I%C2%B2C`
    """

    sda = Port()
    "Synchronous Data Line"
    scl = Port()
    "Synchronous Clock Line"


class SMBus(Port):
    """System Management Bus (SMBus) - Serial Communication Protocol

    see `http://smbus.org/specs/`
    """

    smbclk = Port()
    "Synchronous Clock Line"
    smbdat = Port()
    "Synchronous Data Line"

    smbalert: Port | None = None
    "SMBus Alert# Line"
    smbsus: Port | None = None
    "SMBus Suspend# Line"

    def __init__(self, *, alert: bool = False, sus: bool = False):
        if alert:
            self.smbalert = Port()
        if sus:
            self.smbsus = Port()


class SPI(Port):
    """Serial Peripheral Interface (SPI) - Serial Communication Protocol

    see `https://en.wikipedia.org/wiki/Serial_Peripheral_Interface`
    """

    sck = Port()
    "Synchronous Clock Line"
    cs: Port | None = None
    "Chip Select"
    copi: Port | None = None
    "Controller Out Peripheral In"
    cipo: Port | None = None
    "Controller In Peripheral Out"

    def __init__(self, *, cs=False, copi=True, cipo=True):
        if cs:
            self.cs = Port()
        if copi:
            self.copi = Port()
        if cipo:
            self.cipo = Port()


class WideSPI(SPI):
    """Wide SPI Bundle with configurable data bus width"""

    sck = Port()
    "Synchronous Clock Line"
    data: Sequence[Port]
    "Data Bus"
    cs: Port | None = None
    "Chip Select"

    def __init__(self, width: int, *, cs: bool = False):
        super().__init__(cs=cs, copi=False, cipo=False)
        self.data = [Port() for _ in range(width)]

    @classmethod
    def dual(cls, cs: bool = False):
        return cls(2, cs=cs)

    @classmethod
    def quad(cls, cs: bool = False):
        return cls(4, cs=cs)

    @classmethod
    def octal(cls, cs: bool = False):
        return cls(8, cs=cs)


class OctalSPIwDQS(WideSPI):
    dqs = Port()
    """Data strobe"""

    def __init__(self):
        super().__init__(8, cs=True)


class CANPhysical(Port):
    """CAN Physical Layer Bundle

    This bundle defines the physical layer for the CAN interface
    which consists of a differential pair ``H`` / ``L``
    """

    H = Port()
    "High side of differential pair"
    L = Port()
    "Low side of differential pair"


class CANLogical(Port):
    """CAN Logical Interface Bundle

    This interface from a microcontroller to the PHY is typically a two wire
    interface consisting of a TX and RX line.
    """

    rx = Port()
    "Receive line"
    tx = Port()
    "Transmit line"
    # TODO - Add optional error line ?


class UART(Port):
    """Universal Asynchronous Receiver/Transmitter (UART) Bundle

    see `https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter`
    """

    tx: Port | None = None
    "Transmit Data Line (enabled by default)"
    rx: Port | None = None
    "Receive Data Line (enabled by default)"
    cts: Port | None = None
    "Clear to Send Line"
    rts: Port | None = None
    "Ready to Send Line"
    dtr: Port | None = None
    "Data Terminal Ready Line"
    dsr: Port | None = None
    "Data Set Ready Line"
    dcd: Port | None = None
    "Data Carrier Detect Line"
    ri: Port | None = None
    "Ring Indicator Line"
    ck: Port | None = None
    "Clock Line"
    de: Port | None = None
    "Driver Enable Line"

    def __init__(
        self,
        *,
        tx: bool = True,
        rx: bool = True,
        cts: bool = False,
        rts: bool = False,
        dtr: bool = False,
        dsr: bool = False,
        dcd: bool = False,
        ri: bool = False,
        ck: bool = False,
        de: bool = False,
    ):
        if tx:
            self.tx = Port()
        if rx:
            self.rx = Port()
        if cts:
            self.cts = Port()
        if rts:
            self.rts = Port()
        if dtr:
            self.dtr = Port()
        if dsr:
            self.dsr = Port()
        if dcd:
            self.dcd = Port()
        if ri:
            self.ri = Port()
        if ck:
            self.ck = Port()
        if de:
            self.de = Port()

    @classmethod
    def minimal(cls):
        """Minimal UART Bundle - TX and RX only"""
        return cls()

    @classmethod
    def flowcontrol(cls):
        """UART with RTS/CTS flow control"""
        return cls(rts=True, cts=True)


class I2S(Port):
    """Inter-Integrated Sound (I2S) Bundle - Serial Audio Interface

    see `https://www.nxp.com/docs/en/user-manual/UM11732.pdf`
    """

    sck = Port()
    "Serial Interface Clock"
    ws = Port()
    "Word Select (Left/Right indicator)"
    sd = Port()
    "Serial Data Signal"


class Microwire(Port):
    """Microwire serial communication protocol - subset of SPI"""

    clk = Port()
    "Synchronous Clock"
    cs: Port | None = None
    "Chip Select"
    do: Port | None = None
    "Data Output"
    di: Port | None = None
    "Data Input"

    def __init__(self, *, cs: bool = False, do: bool = False, di: bool = False):
        if cs:
            self.cs = Port()
        if do:
            self.do = Port()
        if di:
            self.di = Port()

    @classmethod
    def four(cls):
        """4-wire Microwire variant - CS, DO, DI"""
        return cls(cs=True, do=True, di=True)

    @classmethod
    def three(cls):
        """3-wire Microwire variant - CS and DO (bidirectional data)"""
        return cls(cs=True, do=True)


class JTAG(Port):
    """JTAG Serial Interface Bundle

    Typically used for debugging/testing integrated circuits.

    This bundle does not include ``TRSTN`` or Target Reset. Use a separate
    ``reset`` bundle to provide that interface on a connector or
    microcontroller.
    """

    tck = Port()
    "Synchronous Clock Line"
    tdi = Port()
    "Data Input Line"
    tdo = Port()
    "Data Output Line"
    tms = Port()
    "State Select Line"


class SWD(Port):
    """Serial Wire Debug Bundle"""

    swdio = Port()
    "Serial Wire Debug Data I/O Line"
    swdclk = Port()
    "Serial Wire Debug Clock Line"
    swo: Port | None = None
    "Serial Wire Output Line"

    def __init__(self, swo: bool = False):
        if swo:
            self.swo = Port()
