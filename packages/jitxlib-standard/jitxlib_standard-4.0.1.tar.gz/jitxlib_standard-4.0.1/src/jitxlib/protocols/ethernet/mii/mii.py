from jitx.net import Port


class MII(Port):
    """Media Independent Interface (MII) Bundle Generator
    see `https://en.wikipedia.org/wiki/Media-independent_interface#Standard_MII`

    Args:
        col: Include collision line
        cs: Include carrier sense line
        tx_er: Include transmit error line
    """

    # explicit list to get a tiny bit more static type checking
    txd = Port(), Port(), Port(), Port()
    "Transmit data bus"
    rxd = Port(), Port(), Port(), Port()
    "Receive data bus"

    tx_clk = Port()
    "Transmit clock for 10/100 MBit"
    tx_en = Port()
    "Transmit enable"

    rx_clk = Port()
    "Receive clock line"
    rx_dv = Port()
    "Receive data valid line"
    rx_er = Port()
    "Receive error line"

    col: Port | None = None
    "Collision"
    cs: Port | None = None
    "Carrier Sense"
    tx_er: Port | None = None
    "Transmit Error"

    def __init__(self, col=False, cs=False, tx_er=False):
        if col:
            self.col = Port()
        if cs:
            self.cs = Port()
        if tx_er:
            self.tx_er = Port()
